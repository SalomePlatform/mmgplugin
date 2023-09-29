from os import system, path
from loggerpy.loggingMld import *

logger = Logger()
logger.set_level("info")

OUTPUT_PLOT_ROOT_PATH = os.path.join('..', 'studies')
OUTPUT_PLOT_PATH = '.'

def set_output_plot_path(p):
    """setter for OUTPUT_PLOT_PATH"""
    global OUTPUT_PLOT_PATH
    OUTPUT_PLOT_PATH = p

def lists_to_dat(filename, X, Y, Z):
    """convert X, Y, and Z (shaped n*1, m*1, n*m) to a .dat file"""
    logger.debug("dat filename : " + filename)
    with open(filename, 'w') as f:
        f.write('# X     Y     Z\n')
        for i in range(len(X)):
            for j in range(len(Y)):
                x_val, y_val, z_val = X[i], Y[j], Z[j][i]
                f.write(f'  {x_val}     {y_val}     {z_val}\n')

def write_gp_script(filename, data_filename, output_filename, Xlabel, Ylabel, Zlabel):
    """write the necessary gp script"""
    logger.debug("gp filename : " + filename)
    logger.debug(f'''set output "{os.path.join(OUTPUT_PLOT_ROOT_PATH, OUTPUT_PLOT_PATH, output_filename)}.png''')
    with open(filename, 'w') as file:

        formatted_str = f'''
set terminal pngcairo size 800,600 enhanced font "Arial,10"
set ticslevel 0
set output "{os.path.join(OUTPUT_PLOT_ROOT_PATH, OUTPUT_PLOT_PATH, "surface", output_filename)}.png"
set title "Surface Visualization of {Zlabel} as a Function of {Xlabel} and {Ylabel}"
set xlabel "{Xlabel}"
set ylabel "{Ylabel}"
set cblabel "{Zlabel}"
set dgrid3d 30,30
set palette defined ( 0.1 "green", 0.25 "blue", 0.4 "red", 0.7 "orange" )
set style lines 100 lt 5 lw 0.5
set pm3d hidden3d 100
set grid
set view 74,200
unset key
set cntrparam levels auto 10
splot '{data_filename}' using 1:2:3 with pm3d, \\
'{data_filename}' using 1:2:3
'''
        file.write(formatted_str)

def write_gp_script_contour(filename, data_filename, output_filename, Xlabel, Ylabel, Zlabel):
    """write the necessary gp script for contours"""
    contour_filename = "contour_" + filename
    contour_output_filename = "contour_" + output_filename
    with open(contour_filename, 'w') as file:

        formatted_str = f'''
set terminal pngcairo size 800,600 enhanced font "Arial,10"
set ticslevel 0
set output "{os.path.join(OUTPUT_PLOT_ROOT_PATH, OUTPUT_PLOT_PATH, "contour", contour_output_filename)}.png"
set title "Contour Visualization of {Zlabel} as a Function of {Xlabel} and {Ylabel}"
set xlabel "{Xlabel}"
set ylabel "{Ylabel}"
set cblabel "{Zlabel}"
set dgrid3d 50,50
set palette rgbformulae 33,13,10
set palette maxcolors 12
set style lines 100 lt 1 lw 1 lc rgb "black"
set pm3d hidden3d 100
set view 74,200
unset key

set lmargin at screen 0.1
set rmargin at screen 0.85
set contour base
set cntrparam level auto 10
unset surface
set pm3d map
set pm3d at b
set view map
unset key
splot '{data_filename}' using 1:2:3

'''
        file.write(formatted_str)

def my_gnu_plot(gp_filename, data_filename, X, Y, Z, Xlabel, Ylabel, Zlabel, output_filename):
    """perform a gnu plot"""
    logger.info("starting plot")
    lists_to_dat(data_filename, X, Y, Z)
    write_gp_script(gp_filename, data_filename, output_filename, Xlabel, Ylabel, Zlabel)
    write_gp_script_contour(gp_filename, data_filename, output_filename, Xlabel, Ylabel, Zlabel)
    system(f'gnuplot -p {gp_filename}')
    logger.info("surface plot created")
    contour_filename = "contour_" + gp_filename
    system(f'gnuplot -p {contour_filename}')
    logger.info("contour plot created")
