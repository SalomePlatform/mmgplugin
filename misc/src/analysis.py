import re

class Analysis:
    def __init__(self):
        self.quality = 0
        self.best = 0
        self.avg = 0
        self.worst = 0
        self.vertices = 0
        self.corners = 0
        self.triangles = 0
        self.edges = 0
        self.ridges = 0
        self.hmin = 0
        self.hmax = 0
        self.box = (0, 0, 0) # (x, y, z)

    def pretty_print(self):
        """Display the content of the analysis"""
        bounding_box_str = f"bounding box: {self.box}" if self.box != (0, 0, 0) else "no bounding box analysis found"
        formatted_str = (
            f"\tQuality: {self.quality}\n"
            f"\tBEST: {self.best}\n"
            f"\tAVRG: {self.avg}\n"
            f"\tWRST: {self.worst}\n"
            f"\tVertices: {self.vertices}\n"
            f"\tCorners: {self.corners}\n"
            f"\tTriangles: {self.triangles}\n"
            f"\tEdges: {self.edges}\n"
            f"\tRidges: {self.ridges}\n"
            f"\thmin: {self.hmin}\n"
            f"\thmax: {self.hmax}\n"
            f"\t{bounding_box_str}"
)
        print(formatted_str)

    def get_results(self, text):
        """From the output of a mmgs analysis, fill the fields"""
        text = text.read()
        quality = "  -- MESH QUALITY   "
        best_avrg_worst = r'\s+BEST\s+([\d.]+)\s+AVRG\.\s+([\d.]+)\s+WRST\.\s+([\d.]+)\s\(\d*\)'
        for line in text.splitlines():
            # overall quality
            if self.quality == 0 and re.match(quality + "[0-9]*$", line):
                self.quality = int(line[len(quality):])

            # detailed quality
            if self.best == 0 or self.avg == 0 or self.worst == 0:
                matches = re.match(best_avrg_worst, line)

                if matches:
                    self.best = float(matches.group(1))
                    self.avg = float(matches.group(2))
                    self.worst = float(matches.group(3))

            # vertices and corners
            if self.vertices == 0 or self.corners == 0:
                values = re.findall(r"\d+", line)
                if "NUMBER OF VERTICES" in line:
                    self.vertices = int(values[0])
                    self.corners = int(values[1])

            # triangles
            if self.triangles == 0:
                values = re.findall(r"\d+", line)
                if "NUMBER OF TRIANGLES" in line:
                    self.triangles = int(values[0])

            # edges and ridges
            if self.edges == 0 or self.ridges == 0:
                values = re.findall(r"\d+", line)
                if "NUMBER OF EDGES" in line:
                    self.edges = int(values[0])
                    self.ridges = int(values[1])

            # hmin and hmax
            if self.hmin == 0 or self.hmax == 0:
                values = re.findall(r"[\d.]+", line)
                if "SMALLEST EDGE LENGTH" in line:
                    self.hmin = float(values[0])
                elif "LARGEST  EDGE LENGTH" in line:
                    self.hmax = float(values[0])

        return self

    def get_medit_results(self, text):
        """From the output of medit, fill the bounding box field"""
        text = text.read()
        for line in text.splitlines():
            if "Bounding box" in line:
                values = re.findall(r"-?[\d.]+", line)
                x = float(values[1]) - float(values[0])
                y = float(values[3]) - float(values[2])
                z = float(values[5]) - float(values[4])
                self.box = (abs(x), abs(y), abs(z))

        return self
