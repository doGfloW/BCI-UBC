function [output] = RMS_classification(data_folder)
    myDir = convertCharsToStrings(data_folder)
    inputTable=readtable(filename); 
    load(rms_KNN_model.mat,rms_KNN_model)
    output = rms_KNN_model.predictFcn(inputTable) 
end
