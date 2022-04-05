clear all
%close all
%% loading data to be read
[file,path] = uigetfile('*.txt');
try
    data = dlmread(file, '\t');
catch
    data = dlmread(file, ',');
end

emg = data (:,9);
markers=data(:,end);
EEG=emg ;
% filltering data
apass= bandpass(EEG,[8 13], 250);
bpass= bandpass(EEG,[13 32], 250); 
% for x= 1:350
%     apass(1,:) = [];
%     apass(end,:) = [];
%     bpass(1,:) = [];
%     bpass(end,:) = [];
%     x=x+1;
% end
l=length(emg); % lenth of data
t=(0:l-1)*1/250; %calcuating time
%% plots
close all
tiledlayout(2,2)
nexttile
hold on
plot(t,EEG);
plot(t,markers);
title('EEG raw Data');
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
legend("EEG","Marker");
hold off
nexttile
hold on
plot(apass,'r');
title('EEG Alpha Data');
plot(markers);
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
hold off
nexttile
hold on
plot(bpass,'c');
plot(markers);
title('EEG Beta Data');
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
hold off
%Frequency plot
fs = 250;
EEG_fft = fft(EEG);
L = length(EEG_fft);
f = (0:L-1)*fs/L;
nexttile
plot(f,abs(EEG_fft));
xlabel('Frequency (Hz)')
ylabel('Amplitude')
title('Frequency Data')
alpha=apass;
beta=bpass;
figure
 for x= 1:450
             alpha(1,:) = [];
             alpha(end,:) = [];
             beta(1,:) = [];
             beta(end,:) = [];
            x=x+1;
 end
hold on
plot(alpha)
plot(beta)
hold off


