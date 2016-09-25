#-*- coding: utf-8


WINDOW_SIZE = (640, 480)


def hex2rgb(hexstr):
    hexstr = hexstr.strip('#')
    intval = 0

    try:
        intval = int(hexstr, 16)
    except ValueError:
        intval = 0

    rgb = []
    for shift in (16, 8, 0):
        value = (intval >> shift) & 0xff
        value /= 255.0
        rgb.append(value)

    return rgb


def init():
    from OpenGL.GL import (
        glClearColor,
        glMatrixMode,
    )
    from OpenGL.GLU import (
        gluOrtho2D,
    )

    from OpenGL.GL import (
        GL_PROJECTION,
    )


    glClearColor(1, 1, 1, 0)
    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(0, WINDOW_SIZE[0], 0, WINDOW_SIZE[1])


def draw_rectangle(pt, w, h, color):
    from OpenGL.GL import (
        glColor3f,
        glBegin,
        glVertex2f,
        glEnd,
    )
    from OpenGL.GL import GL_QUADS

    glColor3f(*color)

    glBegin(GL_QUADS)

    glVertex2f(*pt)             # ccw direction
    glVertex2f(pt[0]+w, pt[1])
    glVertex2f(pt[0]+w, pt[1]+h)
    glVertex2f(pt[0], pt[1]+h)

    glEnd()


def draw_triangle(pts, color):
    from OpenGL.GL import (
        glColor3f,
        glBegin,
        glVertex2f,
        glEnd,
    )
    from OpenGL.GL import GL_TRIANGLES

    assert(len(pts) == 3)

    glColor3f(*color)

    glBegin(GL_TRIANGLES)

    for pt in pts:
        glVertex2f(*pt)

    glEnd()


def draw_scene():
    from OpenGL.GL import (
        glClear,
        glPushMatrix,
        glFlush,
        glPopMatrix,
    )
    from OpenGL.GL import GL_COLOR_BUFFER_BIT

    glClear(GL_COLOR_BUFFER_BIT)
    glPushMatrix()

    home_color = hex2rgb('#7DAD83')
    roof_color = hex2rgb('#CC4F25')
    door_color = hex2rgb('#853A21')
    window_color = hex2rgb('#216C85')

    ground = 25
    left_pad = 50
    width = 300
    height = 300

    draw_rectangle((left_pad, ground), width, height, home_color)
    draw_rectangle((left_pad + width*0.05, ground), width*0.25, height*0.6, door_color)
    draw_rectangle((left_pad + width - width*0.1 - width*0.25, ground + width*0.45), width*0.25, height*0.4, window_color)
    draw_triangle(
        (
            (left_pad, ground + height),
            (left_pad + width, ground + height),
            (left_pad + width/2.0, ground + height + height*0.45)
        ),
        roof_color
    )

    glFlush()
    glPopMatrix()


def main(argv):
    from OpenGL.GLUT import (
        glutInit,
        glutInitDisplayMode,
        glutInitWindowPosition,
        glutInitWindowSize,
        glutCreateWindow,
        glutDisplayFunc,
        glutMainLoop,
    )

    from OpenGL.GLUT import (
        GLUT_SINGLE,
        GLUT_RGB,
    )


    glutInit(argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(0, 0)
    glutInitWindowSize(*WINDOW_SIZE)
    glutCreateWindow('lab02.task01')

    init()

    glutDisplayFunc(draw_scene)
    glutMainLoop()

if __name__ == '__main__':
    import sys

    main(sys.argv)
