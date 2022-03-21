function [output] = RMS_classification(data_folder)
    myDir = convertCharsToStrings(data_folder)
    inputTable=readtable(filename); 
    load(rms_model.mat,RMS_model)
    output = RMS_model.predictFcn(inputTable) 
end
