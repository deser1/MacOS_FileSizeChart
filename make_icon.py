from PIL import Image, ImageDraw

def create_icons():
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rysowanie tła (zaokrąglony kwadrat w stylu macOS)
    rad = 110
    draw.rounded_rectangle((20, 20, size-20, size-20), radius=rad, fill="#ffffff", outline="#d1d1d6", width=6)

    # Rysowanie wykresu kołowego na środku
    margin = 100
    bbox = (margin, margin, size-margin, size-margin)
    
    # Kawałki (wedges) wykresu
    draw.pieslice(bbox, start=-90, end=45, fill="#4a90e2", outline="white", width=8)  # Niebieski
    draw.pieslice(bbox, start=45, end=180, fill="#f5a623", outline="white", width=8)  # Pomarańczowy
    draw.pieslice(bbox, start=180, end=270, fill="#7ed321", outline="white", width=8) # Zielony

    # Zapis w trzech potrzebnych formatach
    img.save("icon.png")
    img.save("icon.ico", format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    
    try:
        img.save("icon.icns", format="ICNS")
        print("Ikony zostały pomyślnie wygenerowane (PNG, ICO, ICNS).")
    except Exception as e:
        print("Błąd zapisu ICNS:", e)

if __name__ == "__main__":
    create_icons()
