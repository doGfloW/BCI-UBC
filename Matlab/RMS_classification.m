function [output] = RMS_classification(VarName)
    T=array2table(VarName); 
    allVars = 1:width(T);
    newNames = append("VarName",string(allVars));
    T = renamevars(T,allVars,newNames);
%     myDir = convertCharsToStrings(VarName)
%     inputTable=readtable(filename); 
    load('rms_KNN_Model.mat')
    output = RMS_KNN_Model.predictFcn(T);
end
