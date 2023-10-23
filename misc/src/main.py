import subprocess
import time
import re
import os
import time
import shutil
from collections import defaultdict
import numpy as np
from math import sqrt
from scipy.fft import fft
from plotter import *
from my_gnuplot import * 
from analysis import Analysis
from misc import *
from loggerpy.loggingMld import *

logger = Logger()
logger.set_level("info")

results_dict = defaultdict(list)
bounding_box_needed = True
logger.info("bounding box calculation : " + str(bounding_box_needed))

def perform_analysis(path):
    """perform an analysis on the file path and return an analysis"""
    file_name = path.split('/')[-1]
    logger.debug("performing analysis on : " + path)
    logger.debug("performing analysis on file : " + file_name)
    # list files
    analysis = Analysis()
    logger.debug(str(perform_mesh_ls(OUTPUT_PATH)))
    logger.debug(str(["mmgs_O3", "-noinsert", "-noswap", "-nomove", path, os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh"), "-v", "5"]))
    with subprocess.Popen(["mmgs_O3", "-noinsert", "-noswap", "-nomove", path, os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh"), "-v", "5"], text=True, stderr = subprocess.PIPE, stdout = subprocess.PIPE) as mmgs_out:
        logger.debug(mmgs_out.stderr.read())
        analysis.get_results(mmgs_out.stdout)
    if bounding_box_needed:
        if re.match(r".*\.o\.mesh", file_name) is not None:
            alter_ego = file_name[:-6] + "mesh"
            logger.debug("alter ego : " + alter_ego)
            analysis.box = results_dict[alter_ego][0].box
        else:
            if len(results_dict[file_name]) == 0:
                with subprocess.Popen(["medit", path], text=True, stderr = subprocess.PIPE, stdout = subprocess.PIPE) as medit_out:
                    analysis.get_medit_results(medit_out.stdout)
            else:
                analysis.box = results_dict[file_name][0].box
    return analysis

def perform_remeshing(path, hausd=None, hgrad=None, hmin=None, hmax=None, hsiz=None):
    """perform the remeshing on the file path"""
    args = []
    if hausd is not None:
        args += ["-hausd", str(hausd)]
    if hgrad is not None:
        args += ["-hgrad", str(hgrad)]
    if hmin is not None:
        args += ["-hmin", str(hmin)]
    if hmax is not None:
        args += ["-hmax", str(hmax)]
    if hsiz is not None:
        args += ["-hsiz", str(hsiz)]
    logger.info("remeshing " + path + ", parameters : " + str(args))
    logger.debug("remesh output : " + os.path.join(OUTPUT_PATH, path.split('/')[-1][:-4] + "o.mesh"))
    logger.debug(str(["mmgs_O3"] + args + [path, os.path.join(OUTPUT_PATH, path.split('/')[-1][:-4] + "o.mesh")]))

    # perform the remeshing
    with subprocess.Popen(["mmgs_O3"] + args + [path, os.path.join(OUTPUT_PATH, path.split('/')[-1][:-4] + "o.mesh")], text=True, stderr = subprocess.PIPE, stdout = subprocess.PIPE) as mesh_process:
        mesh_process.stdout.read()


def perform_hausd_hgrad_variations():
    """observations are done by changing hausd and hgrad"""
    hausd_values = np.linspace(0.005, 0.01, 10)
    hgrad_values = np.linspace(1, 2, 10)
    X, Y = np.meshgrid(hausd_values, hgrad_values)

    quality_measures = np.full_like(X, -1)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(hausd_values):
            for j, _ in enumerate(hgrad_values):
                perform_remeshing(file_path, hausd=hausd_values[i], hgrad=hgrad_values[j], hmin=None, hmax=None)
                value = perform_analysis(output_file_name)
                results_dict[file_name].append(value)

                quality_measures[j][i] = value.quality

                empty_dir()

        # plots
        my_gnu_plot('analysis.gp', 'analysis.dat', hausd_values, hgrad_values, quality_measures, 'hausd', 'hgrad', 'quality', file_name.split('.')[0] + "_hausd_hgrad_quality")

def perform_hmin_hmax_variations():
    """observations are done by changing hmin and max"""
    hmin_values = np.linspace(0.01, 1, 10)
    hmax_values = np.linspace(0.01, 1, 10)
    X, Y = np.meshgrid(hmin_values, hmax_values)

    quality_measures = np.full_like(X, -1)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(hmin_values):
            for j, _ in enumerate(hmax_values):
                if hmax_values[j] <= hmin_values[i]:
                    continue
                perform_remeshing(file_path, hausd=None, hgrad=None, hmin=hmin_values[i], hmax=hmax_values[j])
                value = perform_analysis(output_file_name)
                results_dict[file_name].append(value)

                quality_measures[j][i] = value.quality

                empty_dir()

        # plots
        my_gnu_plot('analysis.gp', 'analysis.dat', hmin_values, hmax_values, quality_measures, 'hmin', 'hmax', 'quality', file_name.split('.')[0] + "_hmin_hmax_quality")

def perform_hmin_hmax_hgrad_variations():
    """observations are done by changing hmax-hmin and hgrad"""
    amplitude = 10
    epsilon = 0.01
    nb_measures = 20
    h_var_values = np.linspace(epsilon, amplitude - epsilon, nb_measures)
    hgrad_values = np.linspace(0.1, 1, 10)
    X, Y = np.meshgrid(h_var_values, hgrad_values)

    quality_measures = np.full_like(X, -1)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(h_var_values):
            for j, _ in enumerate(hgrad_values):
                perform_remeshing(file_path, hausd=None, hgrad=hgrad_values[j], hmin=(amplitude - h_var_values[i]), hmax=(amplitude + h_var_values[i]))
                value = perform_analysis(output_file_name)
                results_dict[file_name].append(value)

                quality_measures[j][i] = value.quality

                empty_dir()

        # plots
        my_gnu_plot('analysis.gp', 'analysis.dat', h_var_values, hgrad_values, quality_measures, 'hmax-hmin', 'hgrad', 'quality', file_name.split('.')[0] + "_hmax_hmin_hgrad_quality")

def perform_hmin_hmax_hausd_variations():
    """observations are done by changing hmax-hmin and hausd"""
    h_var_values = np.linspace(0.01, 0.5, 10)
    hausd_values = np.linspace(0.001, 0.03, 10)
    X, Y = np.meshgrid(h_var_values, hausd_values)

    quality_measures = np.full_like(X, -1)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(h_var_values):
            for j, _ in enumerate(hausd_values):
                perform_remeshing(file_path, hausd=hausd_values[j], hgrad=None, hmin=(1-h_var_values[i]), hmax=(1+h_var_values[i]))
                value = perform_analysis(output_file_name)
                results_dict[file_name].append(value)

                quality_measures[j][i] = value.quality

                empty_dir()

        # plots
        my_gnu_plot('analysis.gp', 'analysis.dat', h_var_values, hausd_values, quality_measures, 'hmax-hmin', 'hausd', 'quality', file_name.split('.')[0] + "_hmax_hmin_hausd_quality")

def perform_3D_graph():
    """hmax-hmin, hgrad, hausd"""
    h_var_values = np.linspace(0.01, 0.5, 5)
    hausd_values = np.linspace(0.001, 0.03, 5)
    hgrad_values = np.linspace(0.1, 1, 5)

    shape = (h_var_values.shape[0], hausd_values.shape[0], hgrad_values.shape[0])
    quality_measures = np.full(shape, -1)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(h_var_values):
            for j, _ in enumerate(hausd_values):
                for k, _ in enumerate(hgrad_values):
                    perform_remeshing(file_path, hausd=hausd_values[j], hgrad=hgrad_values[k], hmin=(1-h_var_values[i]), hmax=(1+h_var_values[i]))
                    value = perform_analysis(os.path.join(OUTPUT_PATH, output_file_name))
                    results_dict[file_name].append(value)

                    quality_measures[i][j][k] = value.quality

                    empty_dir()

        # plots
        plot3D(h_var_values, hausd_values, hgrad_values, quality_measures, 'hmax-hmin', 'hausd', 'hgrad', 'Quality', file_name + '\ntriangles :' + str(liste[0].triangles))


def perform_hausd_variations():
    """observations are done on the diff of hmin and hmax compare to original by changing hausd"""
    hausd_values = np.linspace(0.001, 0.1, 100)
    diff_hmin = np.zeros(hausd_values.shape[0])
    diff_hmax = np.zeros(hausd_values.shape[0])

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        ref_hmin = liste[0].hmin
        ref_hmax = liste[0].hmax
        for i, _ in enumerate(hausd_values):
            perform_remeshing(file_path, hausd=hausd_values[i], hgrad=None, hmin=ref_hmin, hmax=ref_hmax)
            value = perform_analysis(output_file_name)
            results_dict[file_name].append(value)

            diff_hmin[i] = ref_hmin - results_dict[file_name][-1].hmin
            diff_hmax[i] = ref_hmax - results_dict[file_name][-1].hmax

            empty_dir()

        # plots
        classic_plot(hausd_values, diff_hmin, "hausd", "diff_hmin", file_name + '\ntriangles :' + str(liste[0].triangles))
        classic_plot(hausd_values, diff_hmax, "hausd", "diff_hmax", file_name + '\ntriangles :' + str(liste[0].triangles))

def perform_hausd_box_variations():
    """observations are done by changing hausd and the bounding box size"""
    def vol(box):
        return box[0]*box[1]*box[2]
    def max_tuple(box):
        return max(box[0], max(box[1], box[2]))
    def min_tuple(box):
        return min(box[0], min(box[1], box[2]))

    hausd_values = np.linspace(0.005, 0.05, 15)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for j, _ in enumerate(hausd_values):
            perform_remeshing(file_path, hausd=hausd_values[j], hgrad=None, hmin=None, hmax=None)
            value = perform_analysis(output_file_name)
            results_dict[file_name].append(value)

            empty_dir()

    #sort the dictionnary entries by volume, size_min, size_max
    analyses_sorted_by_vol = dict(sorted(results_dict.items(), key=lambda x: vol(x[1][0].box)))
    analyses_sorted_by_max = dict(sorted(results_dict.items(), key=lambda x: max_tuple(x[1][0].box)))
    analyses_sorted_by_min = dict(sorted(results_dict.items(), key=lambda x: min_tuple(x[1][0].box)))

    #store their dimensions
    boxes_sorted_by_vol = np.array([vol(elt[0].box) for name , elt in analyses_sorted_by_vol.items()])
    boxes_sorted_by_max_tuple = np.array([max_tuple(elt[0].box) for name , elt in analyses_sorted_by_max.items()])
    boxes_sorted_by_min_tuple = np.array([min_tuple(elt[0].box) for name , elt in analyses_sorted_by_min.items()])

    Xvol, Yvol = np.meshgrid(boxes_sorted_by_vol, hausd_values)
    Xmax_tuple, Ymax_tuple = np.meshgrid(boxes_sorted_by_max_tuple, hausd_values)
    Xmin_tuple, Ymin_tuple = np.meshgrid(boxes_sorted_by_min_tuple, hausd_values)

    vol_quality_measures = np.full_like(Xvol, -1)
    max_tuple_quality_measures = np.full_like(Xmax_tuple, -1)
    min_tuple_quality_measures = np.full_like(Xmin_tuple, -1)

    i = 0
    for file_name, liste in analyses_sorted_by_vol.items():
        for j, _ in enumerate(hausd_values):
            vol_quality_measures[j][i] = liste[-j].quality
        i += 1

    i = 0
    for file_name, liste in analyses_sorted_by_max.items():
        for j, _ in enumerate(hausd_values):
            max_tuple_quality_measures[j][i] = liste[-j].quality
        i += 1

    i = 0
    for file_name, liste in analyses_sorted_by_min.items():
        for j, _ in enumerate(hausd_values):
            min_tuple_quality_measures[j][i] = liste[-j].quality
        i += 1

    # plots
    my_gnu_plot('analysis.gp', 'analysis.dat', boxes_sorted_by_vol, hausd_values, vol_quality_measures, 'volume', 'hausd', 'quality', "volume_hausd_quality")
    my_gnu_plot('analysis.gp', 'analysis.dat', boxes_sorted_by_max_tuple, hausd_values, max_tuple_quality_measures, 'max size', 'hausd', 'quality', "max_size_hausd_quality")
    my_gnu_plot('analysis.gp', 'analysis.dat', boxes_sorted_by_min_tuple, hausd_values, min_tuple_quality_measures, 'min size', 'hausd', 'quality', "min_size_hausd_quality")

def perform_hgrad_hausd_gnu_plot():
    """perform a gnu plot of the quality with a variation of hgrad and hausd"""
    hausd_values = np.linspace(0.005, 0.03, 20)
    hgrad_values = np.linspace(1, 2, 10)
    X, Y = np.meshgrid(hausd_values, hgrad_values)

    quality_measures = np.full_like(X, -1)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(hausd_values):
            for j, _ in enumerate(hgrad_values):
                perform_remeshing(file_path, hausd=hausd_values[i], hgrad=hgrad_values[j], hmin=None, hmax=None)
                value = perform_analysis(output_file_name)
                results_dict[file_name].append(value)

                quality_measures[j][i] = liste[-1].quality

                empty_dir()

        # plots
        my_gnu_plot('analysis.gp', 'analysis.dat', hausd_values, hgrad_values, quality_measures, 'hausd', 'hgrad', 'quality', file_name.split('.')[0] + "_hausd_hgrad")

def perform_hsiz_hausd_gnu_plot():
    """perform a gnu plot of the quality with a variation of hsiz and hausd"""
    hausd_values = np.linspace(0.001, 0.1, 20)
    hsiz_values = np.linspace(0.1, 2, 10)
    X, Y = np.meshgrid(hausd_values, hsiz_values)

    quality_measures = np.full_like(X, -1)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(hausd_values):
            for j, _ in enumerate(hsiz_values):
                perform_remeshing(file_path, hausd=hausd_values[i], hgrad=None, hmin=None, hmax=None, hsiz=hsiz_values[j])
                value = perform_analysis(output_file_name)
                results_dict[file_name].append(value)

                quality_measures[j][i] = value.quality

                empty_dir()

        # plots
        my_gnu_plot('analysis.gp', 'analysis.dat', hausd_values, hsiz_values, quality_measures, 'hausd', 'hsiz', 'quality', file_name.split('.')[0] + "_hausd_hsiz")

def perform_hsiz_box_variations():
    """observations are done by changing hausd and the bounding box size"""
    def vol(box):
        return box[0]*box[1]*box[2]
    def norm(box):
        return sqrt(box[0]**2 + box[1]**2 + box[2]**2)

    hsiz_values = np.linspace(1, 10, 30)

    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for j, _ in enumerate(hsiz_values):
            perform_remeshing(file_path, hausd=None, hgrad=None, hmin=None, hmax=None, hsiz=hsiz_values[j])
            value = perform_analysis(output_file_name)
            results_dict[file_name].append(value)

            empty_dir()

    #sort the dictionnary entries by volume, size_min, size_max
    analyses_sorted_by_vol = dict(sorted(results_dict.items(), key=lambda x: vol(x[1][0].box)))
    analyses_sorted_by_norm = dict(sorted(results_dict.items(), key=lambda x: norm(x[1][0].box)))

    #store their dimensions
    boxes_sorted_by_vol = np.array([vol(elt[0].box) for name , elt in analyses_sorted_by_vol.items()])
    boxes_sorted_by_norm = np.array([norm(elt[0].box) for name , elt in analyses_sorted_by_norm.items()])

    Xvol, Yvol = np.meshgrid(boxes_sorted_by_vol, hsiz_values)
    Xnorm, Ynorm = np.meshgrid(boxes_sorted_by_norm, hsiz_values)

    vol_quality_measures = np.full_like(Xvol, -1)
    norm_quality_measures = np.full_like(Xnorm, -1)

    i = 0
    for file_name, liste in analyses_sorted_by_vol.items():
        for j, _ in enumerate(hsiz_values):
            vol_quality_measures[j][i] = liste[-j].quality
        i += 1

    i = 0
    for file_name, liste in analyses_sorted_by_norm.items():
        for j, _ in enumerate(hsiz_values):
            norm_quality_measures[j][i] = liste[-j].quality
        i += 1

    # plots
    my_gnu_plot('analysis.gp', 'analysis.dat', boxes_sorted_by_vol, hsiz_values, vol_quality_measures, 'volume', 'hsiz', 'quality', "volume_hsiz_quality")
    my_gnu_plot('analysis.gp', 'analysis.dat', boxes_sorted_by_norm, hsiz_values, norm_quality_measures, 'norm', 'hsiz', 'quality', "norm_hsiz_quality")

def main():
    """main"""

    # first analysis on original data
    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        value = perform_analysis(file_path)
        results_dict[file_name].append(value)

    empty_dir()
    # adapt the files to the analyses you want to produce, and the output plot paths to how you want to sort the files.

    # analyses
    #perform_3D_graph()
    #perform_hausd_variations()
    """
    set_output_plot_path('hsiz_box')
    perform_hsiz_box_variations()

    set_output_plot_path('hausd_hsiz')
    perform_hsiz_hausd_gnu_plot()

    set_output_plot_path('hausd_box')
    perform_hausd_box_variations()

    set_output_plot_path('hausd_hgrad')
    perform_hausd_hgrad_variations()

    set_output_plot_path('hmin_hmax')
    perform_hmin_hmax_variations()

    set_output_plot_path('hmin_hmax_hausd')
    perform_hmin_hmax_hausd_variations()

    set_output_plot_path('hmin_hmax_hgrad')
    perform_hmin_hmax_hgrad_variations()

    hgrad_values = np.linspace(1, 1.4, 100)
    quality_measures = [0]*len(hgrad_values)
    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        execution_time = [0]*len(hgrad_values)

        for i, _ in enumerate(hgrad_values):
            start_time = time.time()
            perform_remeshing(file_path, hausd=None, hgrad=hgrad_values[i], hmin=None, hmax=None, hsiz=None)
            value = perform_analysis(output_file_name)
            results_dict[file_name].append(value)

            quality_measures[i] = value.quality

            end_time = time.time()
            execution_time[i] = (end_time - start_time)*50000

        index = 0
        for i, _ in enumerate(quality_measures):
            if quality_measures[i] > quality_measures[index]:
                index = i

        fig, ax = plt.subplots()

        ax.plot(hgrad_values, quality_measures, label='quality')

        ax.plot(hgrad_values, execution_time, label='time * 50000')

        ax.legend()
        plt.show()

    amplitude = 100
    N_echantillons = 1000

    fs = N_echantillons / amplitude

    h_var_values = np.linspace(0, amplitude, N_echantillons, endpoint=False)
    hgrad = 1
    quality_measures = np.zeros(h_var_values.shape[0])


    for file_path in perform_mesh_ls():
        file_name = file_path.split('/')[-1]
        output_file_name = os.path.join(OUTPUT_PATH, file_name[:-4] + "o.mesh")
        liste = results_dict[file_name]

        for i, _ in enumerate(h_var_values):
            perform_remeshing(file_path, hausd=None, hgrad=hgrad, hmin=(amplitude - h_var_values[i]), hmax=(amplitude + h_var_values[i]))
            value = perform_analysis(output_file_name)
            results_dict[file_name].append(value)

            quality_measures[i] = value.quality

            empty_dir()

        # plots
        classic_plot(h_var_values, quality_measures, "hmax-hmin", "quality", 'fft_' + file_name)

        fft_result = fft(quality_measures)
        freqs = np.fft.fftfreq(len(fft_result), 1/fs)
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(h_var_values, quality_measures)
        plt.title('Signal dans le domaine temporel')
        plt.xlabel('Temps (s)')
        plt.ylabel('Amplitude')

        plt.subplot(2, 1, 2)
        plt.plot(freqs, np.abs(fft_result))
        plt.title('Spectre de fréquence (Module)')
        plt.xlabel('Fréquence (Hz)')
        plt.ylabel('Amplitude')
        plt.xlim(0, fs/2)
        plt.tight_layout()
        plt.savefig('../studies/freq_analysis/freq_' + file_name + '_hmin_hmax_hgrad.png')
        plt.show()
        print("signal:", quality_measures)
        print("fft_result:", fft_result)
        print("freqs:", freqs)
    """

if __name__ == "__main__":
    main()
