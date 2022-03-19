import matlab.engine
m = matlab.engine.start_matlab()
<<<<<<< Updated upstream
data_fold = r'C:\Users\alyna\Documents\ENGR 499\GitHub Repo\Baseline_tests\Mateo_2sec'
ex_fold = r'C:\Users\alyna\Documents\ENGR 499\GitHub Repo\Datasets'
output = m.bandpower_extraction(data_fold, ex_fold)
print(output)
=======
x = m.pythontest(7)
print(x)
>>>>>>> Stashed changes
