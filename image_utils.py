from PIL import Image
import cv2
import numpy as np

def bfs(visited, queue, array, node):
    # I make BFS itterative instead of recursive
    def getNeighboor(array, node):
        neighboors = []
        if node[0]+1<array.shape[0]:
            if array[node[0]+1,node[1]] == 0:
                neighboors.append((node[0]+1,node[1]))
        if node[0]-1>0:
            if array[node[0]-1,node[1]] == 0:
                neighboors.append((node[0]-1,node[1]))
        if node[1]+1<array.shape[1]:
            if array[node[0],node[1]+1] == 0:
                neighboors.append((node[0],node[1]+1))
        if node[1]-1>0:
            if array[node[0],node[1]-1] == 0:
                neighboors.append((node[0],node[1]-1))
        return neighboors

    queue.append(node)
    visited.add(node)

    while queue:
        current_node = queue.pop(0)
        for neighboor in getNeighboor(array, current_node):
            if neighboor not in visited:
                #print(neighboor)
                visited.add(neighboor)
                queue.append(neighboor)

def removeIsland(img_arr, threshold):
    # !important: the black pixel is 0 and white pixel is 1
    while 0 in img_arr:
        x,y = np.where(img_arr == 0)
        point = (x[0],y[0])
        visited = set()
        queue = []
        bfs(visited, queue, img_arr, point)
        
        if len(visited) <= threshold:
            for i in visited:
                img_arr[i[0],i[1]] = 1
        else:
            # if the cluster is larger than threshold (i.e is the text), 
            # we convert it to a temporary value of 2 to mark that we 
            # have visited it. 
            for i in visited:
                img_arr[i[0],i[1]] = 2
                
    img_arr = np.where(img_arr==2, 0, img_arr)
    return img_arr

def cropImage(im):
    colored = im.copy()
    black = 0
    white = 255
    toColor = white
    #UPPER
    for j in range(0, 9):
        for i in range(0,280):
            colored[j,i] = toColor
    #MIDDLE
    for j in range(9, 37):
        for i in range(0, 15):
            colored[j,i] = toColor
        for i in range(40, 55):
            colored[j,i] = toColor
        for i in range(85, 110):
            colored[j,i] = toColor
        for i in range(150, 170):
            colored[j,i] = toColor
        for i in range(200, 225):
            colored[j,i] = toColor
        for i in range(250, 280):
            colored[j,i] = toColor

    #LOWER
    for j in range(37, 50):
        for i in range(0, 280):
            colored[j,i] = toColor
    cv2.imwrite("coloring.png",colored)
    return colored

def algorithm1(img):
    #source: https://medium.com/geekculture/bypassing-captcha-with-breadth-first-search-opencv-and-tesseract-8ea374ee1754
    # Convert to grayscale
    c_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    c_gray = cropImage(c_gray)
    # Median filter
    #out = cv2.medianBlur(c_gray,3)
    
    # Image thresholding
    a = np.where(c_gray>150, 1, c_gray)#all colors supperior to 150 turned in 1 (near to white)
    out = np.where(a!=1, 0, a)#turns all colors less than 150 are turned to black

    # Islands removing with threshold = 30
    pre = np.where(out==1, 255, out)
    out = removeIsland(out, 100)
    sal = np.where(out==1, 255, out)
    cv2.waitKey(0)

    # Median filter
    out = cv2.medianBlur(out,3)

    # Convert to Image type and pass it to tesseract
    im = Image.fromarray(out*255)

    return im