from dotenv import dotenv_values

config = dotenv_values(".env")

with open("esp32/config.h", "w", encoding="utf-8") as f:
    f.write("// ⚙️ Автоматично згенеровано з .env\n")
    f.write(f'#define API_URL "{config["API_URL"]}"\n')
    f.write(f'#define WIFI_SSID "{config["WIFI_SSID"]}"\n')
    f.write(f'#define WIFI_PASSWORD "{config["WIFI_PASSWORD"]}"\n')

print("✅ Файл config.h згенеровано для Arduino.")