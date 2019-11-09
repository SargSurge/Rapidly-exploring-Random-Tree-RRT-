import random
import math
import tkinter as tk
import time


class Point:
    def __init__(self, xcoord, ycoord, frompoint=None, cost=0):
        self.x = xcoord
        self.y = ycoord
        # frompoint is Point() object that was closest to the current point when generated
        self.prev = frompoint
        self.linetoprev = None
        self.to = []
        self.cost = cost

    def distto(self, otherpoint):
        return math.sqrt((self.x - otherpoint.x) ** 2 + (self.y - otherpoint.y) ** 2)

    def add(self, new_point):
        self.to.append(new_point)

    def setLineToPrev(self, newline):
        self.linetoprev = newline

    def updatecost(self, newcost):
        if self.cost < newcost:
            return None
        self.cost = newcost
        for node in self.to:
            self.updatecost(newcost + self.distto(node))


class Graph:
    def __init__(self, rootnode):
        self.root = rootnode
        # this is our list of points that we are gonna do linear search over to find nearest neighbor
        self.points = [rootnode]

    def getIntercept(self, boxes, actualPoint, closestPoint):
        for box in boxes:
            for line in box.lines:
                # print(actualPoint.x,actualPoint.y,closestPoint.x,closestPoint.y)
                if line.collides(actualPoint.x, actualPoint.y, closestPoint.x, closestPoint.y):
                    return True

    def addnode(self, new_point, boxes=[]):
        closestPoint = self.find_nearest_neighbor(new_point)
        actualPoint = Point(closestPoint.x + (new_point.x - closestPoint.x) / closestPoint.distto(new_point),
                            closestPoint.y + (new_point.y - closestPoint.y) / closestPoint.distto(new_point),
                            closestPoint, closestPoint.cost + 1)
        bestPoint = self.find_best_neighbor(actualPoint)
        if self.getIntercept(boxes, actualPoint, closestPoint):
            return None
        if not self.getIntercept(boxes, actualPoint, bestPoint) and bestPoint != closestPoint:
            # print("HELLO")
            bestPoint.add(closestPoint)
            actualPoint.prev = bestPoint
            actualPoint.cost = bestPoint.distto(actualPoint) + bestPoint.cost
        else:
            closestPoint.add(actualPoint)
        self.points.append(actualPoint)
        return actualPoint

    def find_nearest_neighbor(self, new_point):
        distances = []
        min_distance_index = 0
        for neighbor in self.points:
            distances.append(new_point.distto(neighbor))
        min_distance_index = distances.index(min(distances))
        return self.points[min_distance_index]

    # this is me being stupid and trying my own stuff
    def find_best_neighbor(self, new_point):
        totalcosts = []
        min_cost_index = 0
        validpoints = []
        for neighbor in self.points:
            if neighbor.distto(new_point) < 5:
                totalcosts.append(new_point.distto(neighbor) + neighbor.cost)
                validpoints.append(neighbor)
        min_cost_index = totalcosts.index(min(totalcosts))
        # print(min_cost_index)
        return validpoints[min_cost_index]

    def rewire(self, new_node, canvas, boxes):
        for neighbor in self.points:
            if new_node.distto(neighbor) + new_node.cost < neighbor.cost and not self.getIntercept(boxes, new_node,
                                                                                                   neighbor) and new_node.distto(
                    neighbor) < 5:
                # print(neighbor.x, neighbor.y)
                neighbor.prev = new_node
                canvas.delete(neighbor.linetoprev)
                neighbor.setLineToPrev(None)
                newline = canvas.create_line((new_node.x * 10 + 400), (400 - new_node.y * 10), (neighbor.x * 10 + 400),
                                             (400 - neighbor.y * 10))
                neighbor.setLineToPrev(newline)
                canvas.update()
                neighbor.updatecost(new_node.distto(neighbor) + new_node.cost)
                # time.sleep(5)

    def getPath(self, boxes, endpoint, canvas):
        actualPoint = self.find_nearest_neighbor(endpoint)
        if self.getIntercept(boxes, endpoint, actualPoint):
            return None
        path = [actualPoint]
        pathlines = []
        point = actualPoint
        while point != self.root:
            pathlines.append(canvas.create_line((point.x * 10 + 400), (400 - point.y * 10), (point.prev.x * 10 + 400),
                                                (400 - point.prev.y * 10), fill='red'))
            point = point.prev
            path.append(point)
        canvas.update()
        return (path, pathlines)


class CollisionLine:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def between(self, bound1, bound2, x):
        if bound1 > bound2:
            bound1, bound2 = bound2, bound1
        return bound1 <= x and x <= bound2

    def collides(self, x1, y1, x2, y2):
        if x1 == x2:
            if self.x1 == self.x2:
                return x1 == self.x1 and (
                            self.between(y1, y2, self.y1) or self.between(y1, y2, self.y2) or self.between(self.y1,
                                                                                                           self.y2,
                                                                                                           y1) or self.between(
                        self.y1, self.y2, y2))
            if self.between(self.x1, self.x2, x1):
                selfslope = (self.y2 - self.y1) / (self.x2 - self.x1)
                expy = selfslope * (x1 - self.x1) + self.y1
                return self.between(y1, y2, expy) and self.between(self.y1, self.y2, expy)
            else:
                return False
        else:
            # print("case2")
            slope = (y2 - y1) / (x2 - x1)
            if self.x1 == self.x2:
                return self.between(x1, x2, self.x1) and self.between(self.y1, self.y2, slope * (self.x1 - x1) + y1)
            # print("case1")
            # m_1x+b_1 = m_2x+b_2 => x = (b_2-b_1)/(m_1-m_2)
            selfslope = (self.y2 - self.y1) / (self.x2 - self.x1)
            selfb = self.y1 - selfslope * self.x1
            b = y1 - slope * x1
            x = (b - selfb) / (selfslope - slope)
            return self.between(x1, x2, x) and self.between(self.x1, self.x2, x)


class CollisionBox:
    # really basic implementation but idrc
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        if self.x2 < self.x1:
            self.x1, self.x2 = self.x2, self.x1
        if self.y2 < self.y1:
            self.y1, self.y2 = self.y2, self.y1
        self.lines = [CollisionLine(x1, y1, x2, y1)  # bottom line
            , CollisionLine(x1, y2, x1, y1)  # left line
            , CollisionLine(x1, y2, x2, y2)  # top line
            , CollisionLine(x2, y2, x2, y1)]  # right line

    def pointIn(self, p1):
        return not (p1.x <= self.x1 or p1.x >= self.x2) and (p1.y <= self.y1 or p1.y >= self.y2)

    def center(self):
        return Point((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


def drawPoint(canvas, new_point, colors, radius):
    canvas.create_oval((new_point.x * 10 + 400 - radius), (400 - radius - new_point.y * 10),
                       (new_point.x * 10 + 400 + radius), (400 + radius - new_point.y * 10), fill=colors)
    if new_point.prev != None:
        line = canvas.create_line((new_point.x * 10 + 400), (400 - new_point.y * 10), (new_point.prev.x * 10 + 400),
                                  (400 - new_point.prev.y * 10))
        return line
    # else:
    # print(new_point.x,new_point.y)


def go(canvas):
    P = Point(20, 20, None)
    drawPoint(canvas, P, 'blue', 7)
    O = Point(-20, -20, None)
    drawPoint(canvas, O, 'red', 7)
    G = Graph(O)
    n = 0
    randompoint = Point((random.random() - 0.5) * 80, (random.random() - 0.5) * 80, None)
    boxes = [CollisionBox(-12, 8, -8, 12), CollisionBox(-2, -2, 2, 2), CollisionBox(8, -12, 12, -8)]
    rects = []
    for box in boxes:
        rects.append(canvas.create_rectangle(box.x1 * 10 + 400, 400 - box.y1 * 10, box.x2 * 10 + 400, 400 - box.y2 * 10,
                                             fill="blue"))
    dist = 20
    while n < 5000:
        counter = 0
        for box in boxes:
            randompoint = Point((random.random() - 0.5) * 80, (random.random() - 0.5) * 80, None)
            xdir = (randompoint.x - box.center().x) / randompoint.distto(box.center())
            ydir = (randompoint.y - box.center().y) / randompoint.distto(box.center())
            valid = True
            for box2 in boxes:
                if box != box2:
                    if box2.pointIn(Point(box.x1 + xdir, box.y1 + xdir)) or box2.pointIn(
                            Point(box.x2 + xdir, box.y1 + xdir)) or box2.pointIn(
                            Point(box.x1 + xdir, box.y2 + xdir)) or box2.pointIn(Point(box.x2 + xdir, box.y2 + xdir)):
                        valid = False
                        break
            if valid:
                box.x1 += xdir
                box.x2 += xdir
                box.y1 += ydir
                box.y2 += ydir
                canvas.delete(rects[counter])
                rects[counter] = canvas.create_rectangle(box.x1 * 10 + 400, 400 - box.y1 * 10, box.x2 * 10 + 400,
                                                         400 - box.y2 * 10, fill="blue")
                canvas.update()
            counter += 1
        randompoint = Point((random.random() - 0.5) * 80, (random.random() - 0.5) * 80, None)
        newpoint = G.addnode(randompoint, boxes)
        if newpoint != None:
            dist = newpoint.distto(P)
            newline = drawPoint(canvas, newpoint, 'black', 3)
            newpoint.setLineToPrev(newline)
            G.rewire(newpoint, canvas, boxes)
            canvas.update()
            n += 1
            # print(n)
        pathtuple = G.getPath(boxes, P, canvas)
        if pathtuple != None:
            time.sleep(0.001)
            for line in pathtuple[1]:
                canvas.delete(line)
    for pt in path:
        print(pt.x, pt.y)


master = tk.Tk()
w = tk.Canvas(master, width=800, height=800)
w.pack()
canvas_height = 800
canvas_width = 800
master.after(1000, go, w)
tk.mainloop()

