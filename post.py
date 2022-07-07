from normalizer import parse_persian
from post_storage import Post


def parse_data_to_post(token, data) -> Post:
    title, desc = extract_title_desc(data)

    result = extract_widget_list(data)

    credit = result.get("credit", 0)
    rent = result.get("rent", 0)
    surface, age, rooms = extract_main_header(data)
    image_count = extract_image_count(data)

    return Post(
        token,
        title,
        desc,
        credit,
        rent,
        surface,
        age,
        rooms,
        "",
        list(),
        image_count,
    )


def extract_main_header(data):
    list_data_section = get_section(data, "LIST_DATA")
    surface = parse_persian(list_data_section[0]["data"]["items"][0]["value"])
    age = 1401 - parse_persian(list_data_section[0]["data"]["items"][1]["value"])
    rooms = parse_persian(list_data_section[0]["data"]["items"][2]["value"])

    return surface, age, rooms


def extract_title_desc(data):
    title_section = get_section(data, "TITLE")
    title = title_section[0]["data"]["title"]

    desc_section = get_section(data, "DESCRIPTION")
    desc = desc_section[1]["data"]["text"]

    return title, desc


def extract_widget_list(data):
    result = {}
    list_data_section = get_section(data, "LIST_DATA")
    for w in list_data_section:
        typ, d = w["widget_type"], w["data"]
        title = d.get("title", "") or d.get("label", "")

        if title == "اجارهٔ ماهانه":
            result["rent"] = parse_persian(d["value"]) / 1_000_000
        if title == "ودیعه":
            result["credit"] = parse_persian(d["value"]) // 1_000_000
        if title == "برای تبدیل بکشید":
            result["rent"] = parse_persian(d["rent"]["value"]) / 1_000_000
            result["credit"] = parse_persian(d["credit"]["value"]) // 1_000_000
            result["credit_transformed"] = parse_persian(d["credit"]["transformed_value"]) // 1_000_000
        if title == 'مناسب برای':
            result["suitable"] = d["value"]

    return result


def extract_image_count(data):
    try:
        image_section = get_section(data, "IMAGE")
        return len(image_section[0]["data"]["items"])
    except:
        return 0


def get_section(data, section_name: str):
    for s in data["sections"]:
        if s["section_name"] == section_name:
            return s["widgets"]
    return None
