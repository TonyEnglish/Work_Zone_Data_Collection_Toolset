import urllib.request
from io import StringIO
# import cStringIO 
from PIL import Image
# import Image


def get_static_google_map(filename_wo_extension, center=None, zoom=None, imgsize="500x500", imgformat="jpeg",
                          maptype="roadmap", markers=None ):  
    """retrieve a map (image) from the static google maps server 
    
     See: http://code.google.com/apis/maps/documentation/staticmaps/
        
        Creates a request string with a URL like this:
        http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512&maptype=roadmap
&markers=color:blue|label:S|40.702147,-74.015794&sensor=false"""
   
    
    # assemble the URL
    request =  "http://maps.google.com/maps/api/staticmap?" # base URL, append query params, separated by &
    apiKey = 'AIzaSyB6C5lgal0QWlYqp9AS6LHtAqTG9fH9GPA' #'AIzaSyA4urVuj-2wiwNYeih1R_qL_hhXgtnQOjs' # 
    # if center and zoom  are not given, the map will show all marker locations
    request += "key=%s&" % apiKey
    if center != None:
        request += "center=%s&" % center
        #request += "center=%s&" % "40.714728, -73.998672"   # latitude and longitude (up to 6-digits)
        #request += "center=%s&" % "50011" # could also be a zipcode,
        #request += "center=%s&" % "Brooklyn+Bridge,New+York,NY"  # or a search term 
    if center != None:
        request += "zoom=%i&" % zoom  # zoom 0 (all of the world scale ) to 22 (single buildings scale)


    request += "size=%ix%i&" % (imgsize)  # tuple of ints, up to 640 by 640
    request += "format=%s" % imgformat
    # request += "maptype=%s&" % maptype  # roadmap, satellite, hybrid, terrain
    # request += "visible=%s" % "Cambridge"

    # add markers (location and style)
    if markers != None:
        for marker in markers:
                request += "%s&" % marker

    request = request.rstrip('&')
    # #request += "mobile=false&"  # optional: mobile=true will assume the image is shown on a small screen (mobile device)
    # request += "sensor=false"   # must be given, deals with getting loction from mobile device 
    print(request)
    
    urllib.request.urlretrieve(request, filename_wo_extension+"."+imgformat) # Option 1: save image directly to disk
    
    # # Option 2: read into PIL 
    # web_sock = urllib.request.urlopen(request)
    # imgdata = StringIO(web_sock.read()) # constructs a StringIO holding the image
    # try:
    #     PIL_img = Image.open(imgdata)
    
    # # if this cannot be read as image that, it's probably an error from the server,
    # except IOError:
    #     print("IOError:", imgdata.read()) # print error (or it may return a image showing the error"
     
    # # show image 
    # else:
    #     PIL_img.show()
    #     #PIL_img.save(filename_wo_extension+".jpg", "JPEG") # save as jpeg


if __name__ == '__main__':


    # define a series of location markers and their styles
    # syntax:  markers=markerStyles|markerLocation1|markerLocation2|... etc.
    marker_list = []
    marker_list.append("markers=color:blue|label:S|11211|11206|11222") # blue S at several zip code's centers
    marker_list.append("markers=size:tiny|label:B|color:0xFFFF00|40.702147,-74.015794|") # tiny yellow B at lat/long
    marker_list.append("markers=size:mid|color:red|label:6|Brooklyn+Bridge,New+York,NY") # mid-sized red 6 at search location
    # see http://code.google.com/apis/maps/documentation/staticmaps/#Markers


    # make a map around a center
    # get_static_google_map("google_map_example1", center="42.950827,-122.108974", zoom=12, imgsize=(500,500),
                          # imgformat="jpg", maptype="terrain" )


    # get_static_google_map("google_map_example2", center="Empire+State+Building", zoom=14, imgsize=(500,500), markers=marker_list, maptype="hybrid")


    # # make map that shows all the markers
    get_static_google_map("google_map_example3", zoom=10, imgsize=(640,640), imgformat="png", markers=marker_list )

# # thanks to: http://www.daniweb.com/forums/thread65288.html
# from Tkinter import *  # order seems to matter: import Tkinter first
# import Image, ImageTk  # then import ImageTk


# marker_list = []
# marker_list.append("markers=color:blue|label:S|11211|11206|11222") # blue S at several zip code's centers
# marker_list.append("markers=size:tiny|label:B|color:0xFFFF00|40.702147,-74.015794|") # tiny yellow B at lat/long
# marker_list.append("markers=size:mid|color:red|label:6|Brooklyn+Bridge,New+York,NY") # mid-sized red 6 at search location
# # see http://code.google.com/apis/maps/documentation/staticmaps/#Markers


# # make a map around a center
# get_static_google_map("google_map_example1", center="42.950827,-122.108974", zoom=12, imgsize=(500,500),
#                         imgformat="jpg", maptype="terrain" )


# class MyFrame(Frame):
#     def __init__(self, master, im):
#         Frame.__init__(self, master)
#         self.caption = Label(self, text="Some text about the map")
#         self.caption.grid()
#         self.image = ImageTk.PhotoImage(im) # <--- results of PhotoImage() must be stored
#         self.image_label = Label(self, image=self.image, bd=0) # <--- will not work if 'image = ImageTk.PhotoImage(im)'
#         self.image_label.grid()
#         self.grid()

# im = Image.open("mymap.jpg") # read map from disk

# # or you could use the PIL image you created directly via option 2 from the URL request ...
# mainw = Tk()
# mainw.frame = MyFrame(mainw, im)
# mainw.mainloop()