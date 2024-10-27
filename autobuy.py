from steampy.client import SteamClient
from steampy.models import Currency, GameOptions
from secrets import (steam_web_api_key,
                     steam_cookie, steam_login,
                     steam_password, mafile)


def get_steam_client():
    steam_client = SteamClient(steam_web_api_key)
    # cookie_value = steam_cookie
    # steam_client._session.cookies.set("steamLoginSecure", cookie_value)
    steam_client.login(steam_login, steam_password, mafile)
    if steam_client.is_session_alive():
        print('Steam login successful')
        return steam_client
    else:
        print('Steam login failed.')
        user_input = input("Do you want to continue without login? (yes/no): ").strip().lower()
        if user_input == 'yes':
            print("Continuing without login.")
            return None
        else:
            print("Exiting program.")
            exit()


if __name__ == "__main__":
    steam_client = get_steam_client()
    print(steam_client.is_session_alive())
    # response = steam_client.market.buy_item('G3SG1 | Desert Storm (Field-Tested)', '5229334856688702417', 6, 2, GameOptions.CS, Currency.PLN)
