# -*- coding: utf8 -*-
import ezdxf
from math import sin, pi, cos, sqrt

a = 378   # внутренняя длина прямоугольного входа
b = 278   # внутренняя ширина прямоугольного входа
d = 300   # внутренний диаметры груглого выхода
h = 250 - 4   # высота перехода
s = 3     # толщина металла
n = 5     # количество гибов приходящиеся на 1 угол (на сектор 90 гр)
eccentricity = 0   # эксцентриситет по стороне а / координате х
k = 0.4   # коэффициент смещения центрального слоя при гибке

def circles_intersection_points(r0, xy0, r1, xy1, side='right'):
    '''
    Функция находит координаты пересечения двух окружностей на плоскости
    Используется для построения развёртки, когда мы, как будто рисуем две окружности из известных точек, чтобы найти третью
    r0, r1   - радиусы окружностей
    xy0, xy1 - кортежи/списки координаты центров окружностей
    side     - торона отрисовки развёртки, right/left, по муолчанию right
    '''
    x0, y0 = xy0
    x1, y1 = xy1
    d = sqrt((x1 - x0)**2 + (y1 - y0)**2)
    a = (r0**2 - r1**2 + d**2) / (2 * d)
    h = sqrt(r0**2 - a**2)
    x2 = x0 + a * (x1 - x0) / d   
    y2 = y0 + a * (y1 - y0) / d   
    
    # т.к. окружности пересекаются в общем случае в двух точках, выбираем какую из точек принять
    if side == 'right':
        x3 = x2 - h * (y1 - y0) / d
        y3 = y2 + h * (x1 - x0) / d    
    elif side == 'left':
        x3 = x2 + h * (y1 - y0) / d      
        y3 = y2 - h * (x1 - x0) / d          
    return round(x3, 3), round(y3, 3)




def line_length(coord0, coord1):
    '''
    Функция находит длину отрезка по координатам в трёхмерном пространстве
    На вход подаются два кортежа с координатами x, y, z начальной и конечной точек
    coord0 - кортеж вида (x0, y0, z0)
    coord1 - кордеж вида (x1, y1, z1)
    '''
    x0, y0, z0 = coord0
    x1, y1, z1 = coord1
    return sqrt((x0 - x1)**2 + (y0 - y1)**2 + (z0 - z1)**2)

coors_circle_r = []        # координаты полуокружности (правая половина)
r = d / 2 + k * s
for i in range(n):
    alpha = pi / 2 - i * pi / (2 * (n-1))
    x = round(r * cos(alpha), 3)
    y = round(r * sin(alpha), 3)
    coors_circle_r.append((x + eccentricity, y, h))

coors_circle_l = []        # координаты полуокружности (левая половина)
r = d / 2 + k * s
for i in range(n):
    alpha = pi / 2 + i * pi / (2 * (n-1))
    x = round(r * cos(alpha), 3)
    y = round(r * sin(alpha), 3)
    coors_circle_l.append((x + eccentricity, y, h))

half_a = a / 2 + k * s   # половина длины + k толщины металла
half_b = b / 2 + k * s   # половина ширины + k толщины металла

coors_rectangle_r = [(0, half_b, 0), (half_a, half_b, 0), (half_a, 0, 0)]    # Координаты точек прямоугольного входа (правая половина)
coors_rectangle_l = [(0, half_b, 0), (-half_a, half_b, 0), (-half_a, 0, 0)]  # Координаты точек прямоугольного входа (левая половина)

point0 = (0, 0)
point1 = (half_a, 0)
point2 = (-half_a, 0)
small_radius = 2 * r * sin(pi / (4 * (n - 1)))   # малый радиус для построения, равный стороне многогранника

doc = ezdxf.new()       # создаём новый файл
msp = doc.modelspace()  # добавляем новый объект в пространство моделей


# рисуем правую часть
msp.add_line(point0, point1)      # нижняя линия вправо
msp.add_circle(point1, radius=1)  # добавляем окружность радиусом 1 в точку point1 (технологическая особенность данного производства, можно закомментировать)

rad0 = line_length(coors_circle_r[0], coors_rectangle_r[0])        # расстояние между центральной верхней точкой многогранника и центральной точкой прямоугольника
rad1 = line_length(coors_circle_r[0], coors_rectangle_r[1])
new_coor = circles_intersection_points(rad0, point0, rad1, point1) # координата центральной верхней точки развёртки
center_point = new_coor
msp.add_circle(center_point, radius=1)  # добавляем окружность радиусом 1 в точку center_point (технологическая особенность данного производства, можно закомментировать)
msp.add_line(point1, new_coor)          # рисуем линию

for i in range(1, len(coors_circle_r)):   # проходим циклом по части координат и рисуем линии по этим координатам и окружности радиусом 1
    previous_new_coor = new_coor
    rad1 = line_length(coors_circle_r[i], coors_rectangle_r[1])
    new_coor = circles_intersection_points(small_radius, previous_new_coor, rad1, point1)
    msp.add_line(previous_new_coor, new_coor)  
    msp.add_line(point1, new_coor)
    msp.add_circle(new_coor, radius=1)  # добавляем окружность радиусом 1 в точку new_coor

# рисуем финальные 2 линии справа
previous_new_coor = new_coor  
rad0 = line_length(coors_circle_r[n - 1], coors_rectangle_r[2])
rad1 = half_b
new_coor = circles_intersection_points(rad0, previous_new_coor, rad1, point1)
msp.add_line(previous_new_coor, new_coor)   
msp.add_line(point1, new_coor) 


# рисуем левую часть
msp.add_line(point0, point2)      # нижняя линия влево
msp.add_circle(point2, radius=1)  # добавляем окружность радиусом 1 в точку point2
new_coor = center_point
msp.add_line(point2, new_coor)

for i in range(1, len(coors_circle_l)):
    previous_new_coor = new_coor
    rad1 = line_length(coors_circle_l[i], coors_rectangle_l[1])
    new_coor = circles_intersection_points(small_radius, previous_new_coor, rad1, point2, side='left')
    msp.add_line(previous_new_coor, new_coor)  
    msp.add_line(point2, new_coor)
    msp.add_circle(new_coor, radius=1)  # добавляем окружность радиусом 1 в точку new_coor

# рисуем финальные 2 линии слева
previous_new_coor = new_coor  
rad0 = line_length(coors_circle_l[n - 1], coors_rectangle_l[2])
rad1 = half_b
new_coor = circles_intersection_points(rad0, previous_new_coor, rad1, point2, side='left')
msp.add_line(previous_new_coor, new_coor)   
msp.add_line(point2, new_coor) 

doc.saveas('drawing.dxf')


