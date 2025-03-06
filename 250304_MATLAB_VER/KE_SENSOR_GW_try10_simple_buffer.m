clear; clc;

% 시리얼 포트 설정
port = "COM4"; 
baudRate = 1000000;
serialObj = serialport(port, baudRate);
configureTerminator(serialObj, "LF"); 
flush(serialObj); 

% 데이터 저장 변수 초기화
bufferSize = 1000;
voltageData = zeros(1, bufferSize); 
filteredData = zeros(1, bufferSize);
t = 1:bufferSize;

% 저역통과 필터 설정 (Low-Pass Filter)
fs = 240; % 샘플링 주파수 (Hz)
lowCutoff = 3; % 저역통과 필터 차단 주파수 (Hz)
order = 2; % 필터 차수
[b, a] = butter(order, lowCutoff / (fs / 2), 'low'); % 저역통과 필터 생성
filterState = zeros(order, 1); % 필터 상태 저장

% 실시간 플로팅 초기화
figure;
hold on;
rawPlot = plot(t, voltageData, 'Color', [0.7 0.7 0.7], 'DisplayName', 'Raw Data'); 
filteredPlot = plot(t, filteredData, 'r', 'LineWidth', 2, 'DisplayName', 'Low-Pass Filtered');
xlabel('Sample');
ylabel('Voltage (V)');
ylim([0, 0.1]); % Y축 범위 조정
legend;
grid on;
title('Real-Time Low-Pass Filtering with Peak Size Calculation');

% 피크 계산 변수 초기화
peakPlot = plot(NaN, NaN, 'bo', 'MarkerFaceColor', 'b', 'DisplayName', 'Peaks');
dcLine = line([1, bufferSize], [NaN, NaN], 'Color', 'g', 'LineStyle', '--', 'DisplayName', 'DC Value');
currentPeriodText = text(10, 0.08, 'Current Period: N/A', 'FontSize', 12);
avgPeriodText = text(10, 0.075, 'Average Period: N/A', 'FontSize', 12);
currentPeakText = text(10, 0.07, 'Current Peak Size: N/A', 'FontSize', 12);
avgPeakText = text(10, 0.065, 'Average Peak Size: N/A', 'FontSize', 12);

% 피크 계산 변수
peakIntervals = [];
peakSizes = [];

% CSV 파일 설정
csvFileName = 'sensor_data_250223_03.csv';
header = {'Time', 'Raw Data', 'Filtered Data', 'DC Value', 'Current Period', 'Average Period', 'Current Peak Size', 'Average Peak Size'};
writecell(header, csvFileName); % 헤더 저장

% 버퍼 초기화 (CSV에 저장할 데이터 임시 저장)
bufferForWriting = [];

while true
    if serialObj.NumBytesAvailable > 0
        data = readline(serialObj);
        Vout = str2double(data);

        if ~isnan(Vout) % 유효한 데이터만 처리
            % 데이터 저장 (FIFO 방식)
            voltageData = [voltageData(2:end), Vout];

            % 저역통과 필터 적용
            [filteredSample, filterState] = filter(b, a, Vout, filterState);
            filteredData = [filteredData(2:end), filteredSample];

            % 그래프 업데이트
            rawPlot.YData = voltageData;
            filteredPlot.YData = filteredData;

            % DC 값 계산
            dcValue = mean(filteredData);
            set(dcLine, 'YData', [dcValue, dcValue]);

            % 피크 검출
            [peaks, locs, ~, ~] = findpeaks(filteredData, 'MinPeakHeight', 0.02, ...
                                            'MinPeakDistance', 10, 'MinPeakProminence', 0.001);

            if ~isempty(peaks)
                % 피크 위치 업데이트
                set(peakPlot, 'XData', locs, 'YData', peaks);

                % 피크 간의 간격 및 크기 저장
                peakIntervals = [peakIntervals, diff(locs)];
                peakSizes = [peakSizes, abs(peaks - dcValue)];

                if numel(peaks) > 0
                    currentPeakSize = abs(peaks(end) - dcValue);
                    avgPeakSize = mean(peakSizes);

                    % 현재 및 평균 주기 계산
                    if ~isempty(peakIntervals)
                        currentPeriod = peakIntervals(end) / fs;
                        avgPeriod = mean(peakIntervals) / fs;
                        set(currentPeriodText, 'String', ['Current Period: ', num2str(currentPeriod, '%.4f'), ' s']);
                        set(avgPeriodText, 'String', ['Average Period: ', num2str(avgPeriod, '%.4f'), ' s']);
                    end

                    set(currentPeakText, 'String', ['Current Peak Size: ', num2str(currentPeakSize, '%.4f'), ' V']);
                    set(avgPeakText, 'String', ['Average Peak Size: ', num2str(avgPeakSize, '%.4f'), ' V']);
                end
            else
                currentPeriod = NaN;
                avgPeriod = NaN;
                currentPeakSize = NaN;
                avgPeakSize = NaN;
            end

            % CSV 파일에 기록할 데이터 준비
            dataToWrite = {t(end), Vout, filteredSample, dcValue, currentPeriod, avgPeriod, currentPeakSize, avgPeakSize};
            bufferForWriting = [bufferForWriting; dataToWrite];

            % 일정량(100개)이 쌓이면 한 번에 기록
            if size(bufferForWriting, 1) >= 100
                writecell(bufferForWriting, csvFileName, 'WriteMode', 'append');
                bufferForWriting = []; % 버퍼 초기화
            end

            drawnow limitrate;
        end
    end
end
