import requests

def get_skinport_screenshot_link(inspect_link: str) -> str:
    headers = {
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "csinspect/1.0.0 (https://github.com/hexiro/csinspect), Python/3.x, httpx/0.x.x",
    }

    params = {"link": inspect_link}

    response = requests.get("https://screenshot.skinport.com/direct", headers=headers, params=params)
    if response.status_code == 200:
        redirected_url = response.url

        final_url = redirected_url.replace("/direct", "")
        return final_url
    else:
        raise Exception(f"Zapytanie nie powiodło się, kod statusu: {response.status_code}")

inspect_link = "steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20M5237255263905033132A40000951140D12605155372568308049"
result_link = get_skinport_screenshot_link(inspect_link)
print(result_link)

