import numpy as np
import modshogun as sg
def classify_svm(classifier, features, labels, kernel, domain, learn, value, C=1, returnValues=True):
    if learn == 'GridSearch':
        svm = classifier()  
        root = sg.ModelSelectionParameters()
        c1 = sg.ModelSelectionParameters("C1")
        root.append_child(c1)
        c1.build_values(1.0, 10.0, sg.R_LINEAR, 2)

        c2 = sg.ModelSelectionParameters("C2")
        root.append_child(c2)
        c2.build_values(1.0, 10.0, sg.R_LINEAR, 2)

        if kernel.get_name() == 'GaussianKernel':
            param_kernel = sg.ModelSelectionParameters("kernel", kernel)
            width = sg.ModelSelectionParameters("width")
            width.build_values(0.0, 10.0, sg.R_LINEAR, 0.5)
            param_kernel.append_child(width)
            root.append_child(param_kernel)

        elif kernel.get_name() == 'PolyKernel':
            param_kernel = sg.ModelSelectionParameters("kernel", kernel)
            degree = sg.ModelSelectionParameters("degree")
            if value:
                degree.build_values(value[0], value[1], sg.R_LINEAR)
            else:
                degree.build_values(0, 5, sg.R_LINEAR)
            param_kernel.append_child(degree)
            root.append_child(param_kernel)

        elif kernel.get_name() == 'LinearKernel':
            param_kernel = sg.ModelSelectionParameters("kernel", kernel)
            root.append_child(param_kernel)

        pos=0
        neg=0
        for i in range(0, labels.get_num_labels()):
            if labels.get_label(i)==1:
                pos+=1
            else:
                neg+=1
        if pos<2 or neg<2:
            class LabelsError(Exception):
                pass
            raise LabelsError('Need at least two labels from one class')
        elif pos<3 or neg<3:
            splitting_strategy = sg.StratifiedCrossValidationSplitting(labels, 2)
        else:
            splitting_strategy = sg.StratifiedCrossValidationSplitting(labels, 3)
        evaluation_criterium = sg.ContingencyTableEvaluation(sg.ACCURACY)
        cross = sg.CrossValidation(svm, features, labels, splitting_strategy, evaluation_criterium)
        cross.set_num_runs(2)
        grid_search = sg.GridSearchModelSelection(cross, root)
        best_combination = grid_search.select_model()
        best_combination.apply_to_machine(svm)

    else:
        svm = classifier(C, kernel, labels) 
        
    svm.train(features)
    
    size = 100
    x1 = np.linspace(domain['horizontal'][0], domain['horizontal'][1], size)
    y1 = np.linspace(domain['vertical'][0], domain['vertical'][1], size)
    x, y = np.meshgrid(x1, y1)
    
    test = sg.RealFeatures(np.array((np.ravel(x), np.ravel(y))))
    kernel.init(features, test)
   
    if returnValues:
        out = svm.apply(test).get_values()
    else:
        out = svm.apply(test).get_labels()
    z = out.reshape((size, size))
    z = np.transpose(z)
    return x, y, z
