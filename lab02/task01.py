#-*- coding: utf-8


WINDOW_SIZE = (640, 480)
NVERT = 128


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


def draw_circle(pt, r, color):
    from math import (
        pi,
        cos,
        sin,
    )

    from OpenGL.GL import (
        glColor3f,
        glBegin,
        glVertex2f,
        glEnd,
    )
    from OpenGL.GL import GL_TRIANGLE_FAN

    assert(r > 0)

    glColor3f(*color)

    glBegin(GL_TRIANGLE_FAN)

    glVertex2f(*pt)

    for i in range(NVERT+1):
        angle = 2*pi / NVERT * i
        glVertex2f(cos(angle)*r+pt[0], sin(angle)*r+pt[1])

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

    axis = 100
    body_color = (0.8, 0.8, 0.8)
    hat_color = (0, 0, 0.8)

    draw_circle((axis, 100), 50, body_color)
    draw_circle((axis, 100 + 50 + 35), 35, body_color)
    draw_circle((axis, 100 + 50 + 35*2 + 20), 20, body_color)

    bottom = 100 + 50 + 35*2 + 20*2
    draw_triangle(
        (
            (axis + 40, bottom),
            (axis, bottom + 40),
            (axis - 40, bottom),
        ),
        hat_color,
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
