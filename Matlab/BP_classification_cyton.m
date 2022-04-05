function [output] = BP_classification_cyton(VarName)
    T=array2table(VarName); 
    allVars = 1:width(T);
    newNames = append("VarName",string(allVars));
    T = renamevars(T,allVars,newNames);
%     myDir = convertCharsToStrings(VarName)
%     inputTable=readtable(filename); 
    load('cyton_bp_model.mat')
    output = cyton_bp_model.predictFcn(T);
end
