# TCT-gmap
This python program will generate a csv file that can be imported onto google map to plot a lot boundary based on information from a typical land title in the Philippines.

Note that you have to do the data input inside the program as I have no time to write an interface for data input yet.

As mentioned, the program will generate a csv file that can be imported onto google map. This is done as follow:
1. Open google map; select "Your places"
2. From "LISTS  LABELED VISITED MAPS", select "MAPS"
3. At the bottom, select "CREATE MAP"
4. In the "Untitled layer" box, select "Import"
5. Drag & drop (or select) the generated csv file to be imported
6. Click/Check the WKT box; select "Continue"
7. Select the "name" button; select "Finish"
8. DONE! Hopefully, all goes well up to this point.
9. If you select the "Lot" element, it will show you the closure error and the lot area
10. The lot area is calculated directly by google map - this is an extra check
11. Contact me if you have a problem
