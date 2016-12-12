# -*- coding: utf-8 -*-


import csv, pyodbc
from OpenGL import GL, GLU, GLUT


WINDOW_SIZE = (640, 480)
LINES_POINTS = []
INITIAL_TRANS = [0, 0]
INITIAL_SCALE = 1.0
ARC_APPROX_PRECISION = 16

scene_trans = INITIAL_TRANS.copy()
scene_scale = INITIAL_SCALE


def initOpenGL(argv):
    GLUT.glutInit(argv)
    GLUT.glutInitDisplayMode(GLUT.GLUT_SINGLE | GLUT.GLUT_RGB)
    GLUT.glutInitWindowPosition(0, 0)
    GLUT.glutInitWindowSize(*WINDOW_SIZE)
    GLUT.glutCreateWindow(b'cw')

    GL.glClearColor(1, 1, 1, 0)

    GL.glViewport(0, 0, *WINDOW_SIZE)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GLU.gluOrtho2D(0, WINDOW_SIZE[0], 0, WINDOW_SIZE[1])
    GL.glMatrixMode(GL.GL_MODELVIEW)

    GLUT.glutDisplayFunc(draw_scene)
    GLUT.glutSpecialFunc(special_keys)
    GLUT.glutMainLoop()


def special_keys(key, *_):
    global scene_trans, scene_scale

    if key == GLUT.GLUT_KEY_UP:
        scene_trans[1] += (WINDOW_SIZE[1] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_DOWN:
        scene_trans[1] -= (WINDOW_SIZE[1] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_RIGHT:
        scene_trans[0] += (WINDOW_SIZE[0] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_LEFT:
        scene_trans[0] -= (WINDOW_SIZE[0] * scene_scale * 0.1)
    elif key == GLUT.GLUT_KEY_PAGE_UP:
        scene_scale += 0.05
    elif key == GLUT.GLUT_KEY_PAGE_DOWN:
        scene_scale = max(0, scene_scale - 0.05)
    elif key == GLUT.GLUT_KEY_HOME:
        scene_trans = INITIAL_TRANS.copy()
        scene_scale = INITIAL_SCALE

    print('scale:', scene_scale, 'trans:', scene_trans)

    GLUT.glutPostRedisplay()


def prepare_scene(path):
    import pprint

    global LINES_POINTS

    LINES_POINTS = path.GetPoints()

    print('LINES_POINTS:')
    pprint.pprint(LINES_POINTS)


def draw_scene():
    global scene_trans, scene_scale, LINES_POINTS

    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    GL.glLoadIdentity()

    GL.glPushMatrix()

    GL.glTranslatef(scene_trans[0], scene_trans[1], 0)
    GL.glScale(scene_scale, scene_scale, scene_scale)

    GL.glColor3f(0, 0, 0)
    GL.glBegin(GL.GL_LINES)

    for pt in LINES_POINTS:
        GL.glVertex2f(*pt)

    GL.glEnd()

    GL.glPopMatrix()

    GL.glFlush()


class path:
    '''Это контур и работа с ним'''
    def __init__(self):
        self._segments=[]

    def Add(self,seg):
        '''Добавить сегмент в контур'''
        self._segments.append(seg)
        return

    def GetPoints(self):
        pts = []

        for seg in self._segments:
            pts += seg.GetPoints()

        return pts


class point:
    '''Это класс точка'''
    def __init__(self,x=0,y=0):
        self._x=x
        self._y=y

    def Set(self,x,y):
        self._x=x
        self._y=y

    def Get(self):
        return (self._x,self._y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __str__(self):
        return '(%r, %r)' % (self._x, self._y)

class database():
    '''Этот класс читает данные из базы'''

    def GetFromBase(self,pathdb, path,unitpos):
        '''Читает набор точек из pathdb контура path панели unitpos
        paramID, UnitPos, HoldTable, Hold1, Hold2, hold3, ParamName, ParamType, NumValue, StrValue
        '''
        # DRV = '{Microsoft Access Driver (*.mdb)}'
        DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
        PWD = ''

        # connect to db
        con = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(DRV,pathdb,PWD))
        cur = con.cursor()

        # run a query and get the results
        sqlstr='''SELECT Hold1, Hold2, hold3, ParamName, NumValue FROM TParams,TPaths WHERE HoldTable='TPaths' AND TParams.UnitPos={}
 AND TParams.Hold1=TPaths.PathID AND TPaths.PanelPos=TParams.UnitPos AND IsTCuts=0 AND
 TPaths.PathID={} AND Hold2>0 ORDER BY ParamID'''.format(unitpos, path)
        rows = cur.execute(sqlstr).fetchall()   # здесь у нас вообще все подряд параметры
        cur.close()
        con.close()
        return rows

class segment:
    '''Это сегмент контура'''
    pass

class linesegment (segment):
    '''Это сегмент отрезок'''
    def __init__(self,beg=point(0,0),end=point(0,0)):
        self._beg=beg
        self._end=end

    def Set(self,beg=point(0,0),end=point(0,0)):
        self._beg=beg
        self._end=end

    def Get(self):
        return (self._beg,self._end)

    def GetPoints(self):
        return (self._beg.Get(), self._end.Get())

    def __str__(self):
        return 'line %s -> %s' % (self._beg, self._end)

class arcsegment (segment):
    '''Это сегмент дуга'''

    # source: http://algolist.manual.ru/maths/geom/equation/Circle.cpp

    EPSILON = 10 ** -9

    def __init__(self,beg=point(0,0),end=point(0,0), mid=point(0,0)):
        self._beg=beg           # pt1
        self._end=end           # pt3
        self._mid=mid           # pt2

        self._center = point(0, 0)
        self._radius = -1

        if not self._is_prependicular(beg, mid, end):
            self._calc_circle(beg, mid, end)
        elif not self._is_prependicular(beg, end, mid):
            self._calc_circle(beg, end, mid)
        elif not self._is_prependicular(mid, beg, end):
            self._calc_circle(mid, beg, end)
        elif not self._is_prependicular(mid, end, beg):
            self._calc_circle(mid, end, beg)
        elif not self._is_prependicular(end, mid, beg):
            self._calc_circle(end, mid, beg)
        elif not self._is_prependicular(end, beg, mid):
            self._calc_circle(end, beg, mid)

    def _is_prependicular(self, pt1, pt2, pt3):
        yda = pt2.y - pt1.y
        xda = pt2.x - pt1.x
        ydb = pt3.y - pt2.y
        xdb = pt3.x - pt2.x

        if abs(xda) <= self.EPSILON and abs(ydb) <= self.EPSILON:
            return False

        if abs(yda) <= self.EPSILON:
            return True
        elif abs(ydb) <= self.EPSILON:
            return True
        elif abs(xda) <= self.EPSILON:
            return True
        elif abs(xdb) <= self.EPSILON:
            return True

        return False

    @staticmethod
    def _length(pt1, pt2):
        from math import sqrt

        return sqrt((pt2.x - pt1.x)**2 + (pt2.y - pt1.y)**2)

    def _calc_circle(self, pt1, pt2, pt3):
        yda = pt2.y - pt1.y
        xda = pt2.x - pt1.x
        ydb = pt3.y - pt2.y
        xdb = pt3.x - pt2.x

        if abs(xda) <= self.EPSILON and abs(ydb) <= self.EPSILON:
            cx = 0.5 * (pt2.x + pt3.x)
            cy = 0.5 * (pt1.y + pt2.y)

            self._center = point(cx, cy)
            self._radius = self._length(self._center, pt1)

            return True

        aSlope = yda / xda
        bSlope = ydb / xdb

        if abs(aSlope - bSlope) <= self.EPSILON:
            return False

        cx = (
            aSlope * bSlope * (pt1.y - pt3.y) \
            + bSlope * (pt1.x + pt2.x) \
            - aSlope * (pt2.x + pt3.x)
        ) / (
            2 * (bSlope - aSlope)
        )
        cy = -1 * (cx - (pt1.x + pt2.x) / 2) / aSlope + (pt1.y + pt2.y) / 2

        self._center = point(cx, cy)
        self._radius = self._length(self._center, pt1)

        return True

    def Set(self,beg=point(0,0),end=point(0,0), mid=point(0,0)):
        self._beg=beg
        self._end=end
        self._mid=mid

    def Get(self):
        return (self._beg,self._end, self._mid)

    def _get_dummy_points(self):
        return (
            self._beg.Get(),
            self._mid.Get(),
            self._mid.Get(),
            self._end.Get()
        )

    def _ox_angle(self, pt):
        from math import atan2, pi

        rad = atan2(pt.y - self._center.y, pt.x - self._center.x)
        if rad < 0:
            rad += (2 * pi)

        grad = rad * 360 / (2 * pi)

        return (rad, grad)

    def _approximate_arc(self, precision=ARC_APPROX_PRECISION):
        from math import atan2, sqrt, pi, cos, sin

        print('approximate %r' % str(self))
        print('center %r; radius %r' % (str(self._center), self._radius))

        beg, bega = self._ox_angle(self._beg)
        mid, mida = self._ox_angle(self._mid)
        end, enda = self._ox_angle(self._end)

        print(
            'a {beg} ({bega}) -- {mid} ({mida}) -- {end} ({enda})'.format(
                beg=beg, bega=bega,
                mid=mid, mida=mida,
                end=end, enda=enda,
            )
        )

        ccw = mid - beg
        if ccw >= 0:
            ccw = True
        else:
            ccw = False

        # fix non-monotone end values
        if end < mid and ccw:
            end += (2 * pi)
            enda += 360
        elif end > mid and not ccw:
            end -= (2 * pi)
            enda -= 360

        print(
            'fixed a (ccw: {ccw}) {beg} ({bega}) -- {mid} ({mida}) -- {end} ({enda})'.format(
                ccw=ccw,
                beg=beg, bega=bega,
                mid=mid, mida=mida,
                end=end, enda=enda,
            )
        )


        distance = end - beg
        delta = distance / precision

        print('dist {dist}; da {da}'.format(dist=distance, da=delta))

        ret = [self._beg.Get()]

        for i in range(1, precision):
            angle = beg + delta * i

            x = cos(angle) * self._radius + self._center.x
            y = sin(angle) * self._radius + self._center.y

            pt = point(x, y).Get()
            ret.append(pt)
            ret.append(pt)

        ret.append(self._end.Get())

        print('')

        return ret

    def GetPoints(self):
        if self._radius > 0:
            return self._approximate_arc()

        return self._get_dummy_points()

    def __str__(self):
        return 'arc %s -> %s -> %s' % (self._beg, self._mid, self._end)

class SegmentCreator:
    '''Это фабрика по созданию сегметнтов'''
    def CreateSegment(self, rows):
        '''По набору строк возвращаем сегмент нужного типа'''
        for coords in rows:      # Кординаты концов сегмента
            stype=coords[1]     # тип 1 - отрезок, 2 - дуга
            varariable=coords[3]    # Имя параметра
            globals()[varariable]=coords[4]  # Создаем перменную с именем параметра
        if (stype==1):  # Отрезок
            seg=linesegment(point(X1,Y1),point(X2,Y2))
        elif (stype==2):    # Дуга
            seg=arcsegment(point(X1,Y1), point(X2,Y2), point(XM,YM))
        else:   # Не пойми что
            seg=None
            assert(True)
        print('created', str(seg))
        return seg

    def ParseRows(self,rows):
        '''По набору строк rows возвращает набор строк со строками для одного сегмента'''
        lines=[]    # Набор строк со строками одного сегмента - контур целиком. Возвращаемое значение
        line=[]     # Строка с данными для одного сегмента
        hold3=1     # Первый сегмент - всегда единица
        for row in rows:            # Организуем цикл по строкам из базы данных
            if hold3!=row[2]:       # Если запись относится к рассматриваемому сегменту
                lines.append(line)  # прочитанные данные помещаем в выходное значение
                line=[]             # Обнуляем данные по сегменту
            line.append(row)    # Добавляем данные
            hold3=row[2]            # А здесь хранится номер рассматриваемого сегмента
        lines.append(line)
        return lines

def main(argv):
# set up some constants

  import os.path

  global LINES_POINTS

  MDB = argv[1]
  assert(os.path.exists(MDB))
  MDB = os.path.abspath(MDB)

  DRV = '{Microsoft Access Driver (*.mdb)}'
  PWD = ''

  PanelPos=int(argv[2])        # Номер панели (PanelPos в таблице TPaths)
  PathPos=1         # Номер контура (PathID в таблице TPaths)
  base=database()
  rows=base.GetFromBase(MDB,PathPos,PanelPos)

  sg=SegmentCreator()
  lines=sg.ParseRows(rows)
  pat=path()
  for line in lines:
    seg=sg.CreateSegment(line)
    pat.Add(seg)

  print('\nprepare scene and draw\n')

  prepare_scene(pat)
  initOpenGL(argv)

if __name__ == '__main__':
    import sys

    main(sys.argv)
