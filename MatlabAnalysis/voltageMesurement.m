clear;
clc;
close all;

data = readmatrix("Book1.xlsx");

pwcP = data(:,1);
voltageP = data(:,2);

pP = polyfit(voltageP, pwcP, 1);
% y = p(1)*x + p(2)
pwcP_fit = polyval(pP, voltageP);


plot(voltageP, pwcP, '-o');
hold on;
plot(voltageP, pwcP_fit, '-r');
grid on;

% pwcN = data(:,4);
% voltageN = data(:,5);
% 
% pN = polyfit(voltageN, pwcN, 1);
% % y = p(1)*x + p(2)
% pwcN_fit = polyval(pN, voltageN);

% plot(voltageN, pwcN, '-o');
% hold on;
% plot(voltageN, pwcN_fit, '-r');
% grid on;