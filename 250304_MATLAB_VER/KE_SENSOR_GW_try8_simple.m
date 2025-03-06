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
lowCutoff = 2; % 저역통과 필터 차단 주파수 (Hz)
order = 2; % 필터 차수
[b, a] = butter(order, lowCutoff / (fs / 2), 'low'); % 저역통과 필터 생성
filterState = zeros(order, 1); % 필터 상태 저장

% 실시간 플로팅 초기화
figure;
hold on;
rawPlot = plot(t, voltageData, 'Color', [0.7 0.7 0.7], 'DisplayName', 'Raw Data'); 
filteredPlot = plot(t, filteredData, 'b', 'DisplayName', 'Low-Pass Filtered'); 
xlabel('Sample');
ylabel('Voltage (V)');
ylim([0, 0.1]); % Y축 범위 조정
legend;
grid on;
title('Real-Time Low-Pass Filtering with Detailed Peaks');

% 피크 계산 변수 초기화
peakPlot = plot(NaN, NaN, 'ro', 'MarkerFaceColor', 'r', 'DisplayName', 'Peaks'); % 피크를 표시할 plot 객체

% 실시간 데이터 수신 및 필터 적용 루프
while true
    if serialObj.NumBytesAvailable > 0
        data = readline(serialObj); % 아두이노에서 데이터 읽기
        Vout = str2double(data); % 숫자로 변환

        if ~isnan(Vout) % 유효한 데이터만 처리
            % 데이터 저장 (FIFO 방식)
            voltageData = [voltageData(2:end), Vout];

            % 저역통과 필터 적용
            [filteredSample, filterState] = filter(b, a, Vout, filterState);
            filteredData = [filteredData(2:end), filteredSample];

            % 그래프 업데이트
            rawPlot.YData = voltageData;
            filteredPlot.YData = filteredData;

            % 플롯된 데이터에 대해서만 피크 찾기
            [peaks, locs, widths, proms] = findpeaks(filteredData, 'MinPeakHeight', 0.02, ...
                                                      'MinPeakDistance', 10, 'MinPeakProminence', 0.001, ...
                                                      'WidthReference', 'halfheight');
            % 피크가 있을 경우, scatter로 표시 (기존 피크는 삭제)
            if ~isempty(peaks)
                set(peakPlot, 'XData', locs, 'YData', peaks);
            end

            % 그래프 업데이트
            drawnow limitrate;
        end
    end
end
