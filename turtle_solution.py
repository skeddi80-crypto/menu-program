import math

def solve():
    # Читаем из файла INPUT.TXT
    with open("INPUT.TXT", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if not lines:
        return
    
    x, y = 0.0, 0.0
    angle = 0.0  # градусы, направление вдоль OX
    points = [(0.0, 0.0)]
    
    for line in lines[1:]:
        line = line.strip()
        if not line or line == "done()":
            continue
        
        if line.startswith("left("):
            angle += float(line[5:-1])
        elif line.startswith("right("):
            angle -= float(line[6:-1])
        elif line.startswith("forward("):
            d = float(line[8:-1])
            rad = math.radians(angle)
            x += d * math.cos(rad)
            y += d * math.sin(rad)
            points.append((x, y))
    
    # Вычисляем площадь по формуле Гаусса (шнурка)
    area = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    
    area = abs(area) / 2.0
    
    # Записываем результат в OUTPUT.TXT
    with open("OUTPUT.TXT", "w", encoding="utf-8") as f:
        # Если число целое, пишем без .0
        if abs(area - round(area)) < 1e-9:
            f.write(str(int(area)))
        else:
            result = f"{area:.10f}".rstrip('0').rstrip('.')
            f.write(result)

if __name__ == "__main__":
    solve()