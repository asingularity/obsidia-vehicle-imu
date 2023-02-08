%peter.petre@gmail.com, started on 2-7-23

    clear all
    
%input*********************************************************************                
    load('mfiltd1.mat');    %loading in saved matched filter for event 1 
    load('mfiltd2.mat');    %loading in saved matched filter for event 2 
    load('mfiltd3.mat');    %loading in saved matched filter for event 3 
    load('mfiltd4.mat');    %loading in saved matched filter for event 4 
    
    load('2023-02-02T11_15_18.286677_0_accelerometer.mat'); %IMU data ->
                        %colums are: [timestamp | X | Y | Z]
    load('2023-02-02T11_15_18.286677_0_ground_truth_events.mat');    %ground truth ->
                        %columns are [timestamp | event_type], 
                        %where event type descriptors are: end of event -> 0:stop 
                        %beginning of event-> 1:accelerate, 2:turn,3:swerve
                        %rigth, 4:swerve left
                        
    tcal=6;             %available calibration time at the beginning of recording in sec
                        %time length of the static state of the accelerometer    
    THdet1=7.9853;      %detection threshold for matched filter1 
    THdet2=3.3;         %detection threshold for matched filter2 
    THdet3=3.1;         %detection threshold for matched filter3 
    THdet4=4.0;         %detection threshold for matched filter4       
    fs=410.3614;         %sampling rate that best matches to the actual samples
    
%**************************************************************************    
%START data pre-processing*************************************************
%**************************************************************************
    Np=length(accelerometer);   %length of data                                            
    t =accelerometer(1:Np,1)'-accelerometer(1,1);   %time points in sec
                                                    %time axes now starts at 0sec 
    te=ground_truth_events(:,1)'-accelerometer(1,1);%time points in sec
                                                    %time axes now starts at 0sec
    le=length(te);      %length of te                                               
    e=ground_truth_events(:,2)';    %event code                                                 
    axo=accelerometer(1:Np,2)'; %x component of linear acceleration (original)
    ayo=accelerometer(1:Np,3)'; %y component of linear acceleration (original)
    azo=accelerometer(1:Np,4)'; %z component of linear acceleration (original)
             
    dts=1/fs;           %uniform sampling interval in sec
    tu=dts:dts:t(Np);   %uniform time points in sec
    lu=length(tu);      %length of uniformly sampled time series 
    
    for ii=1:le
       INDte(ii)=find(abs(tu-te(ii))<dts/2);   %finding indeces for te in tu
    end
    
%data calibration**********************************************************    
    axocal=axo(1:round(tcal*fs));  %x-acceleration in [0 tcal] 
    ayocal=ayo(1:round(tcal*fs));  %y-acceleration in [0 tcal] 
    azocal=azo(1:round(tcal*fs));  %z-acceleration in [0 tcal] 

        axom=mean(axocal);      %mean value of x-acceleration in [0 tcal] 
        ayom=mean(ayocal);      %mean value of y-acceleration in [0 tcal]
        azom=mean(azocal);      %mean value of z-acceleration in [0 tcal] 
        
    th=atan(ayom/azom);             %rotating around the x-axis to make ayom=0
    Rx=[1,0,0;0,cos(th),-sin(th);0,sin(th),cos(th)];    %rotation matrix about the x axis
        acalrotx=Rx*[axocal;ayocal;azocal];     %rotating IMU cal data about the x axis by th
        axorotxm=mean(acalrotx(1,:));     %mean value of rotated x-acceleration in [0 tcal] 
        ayorotxm=mean(acalrotx(2,:));     %mean value of rotated y-acceleration in [0 tcal]
        azorotxm=mean(acalrotx(3,:));     %mean value of rotated z-acceleration in [0 tcal]
        
    ph=atan(-axorotxm/azorotxm);    %rotating around the y-axis to make axorotxm=0            
    Ry=[cos(ph),0,sin(ph);0,1,0;-sin(ph),0,cos(ph)];    %rotation matrix about the y axis
    
        Arot=Ry*Rx*[axo;ayo;azo];   %rotating IMU data about both x & y axis
        ax=Arot(1,:);   %new x data where both x and y components of the calibration data =0
        ay=Arot(2,:);   %new y data where both x and y components of the calibration data =0
        az=Arot(3,:);   %new z data where both x and y components of the calibration data =0
        
%    Rz=[cos(th),-sin(th),0;sin(th),cos(th),0;0,0,1];    %rotation matrix about the z axis        
    
%resampling data uniformly with fs ****************************************        
        uax=interp1(t,ax,tu,'pchip');  %uniformly sampled version of PC
        uay=interp1(t,ay,tu,'pchip');  %uniformly sampled version of PC

%**************************************************************************    
%END data pre-processing***************************************************
%**************************************************************************        
        
%**************************************************************************    
%START REAL-TIME DETECTION AND CLASSIFICATION ALG.*************************
%**************************************************************************
%matched filer parameters**************************************************    
    lm1=length(mfiltd1);    %length of mfilt1
    lm2=length(mfiltd2);    %length of mfilt2
    lm3=length(mfiltd3);    %length of mfilt3
    lm4=length(mfiltd4);    %length of mfilt4
    INDdet1=[];             %storing detected event1's time
    INDdet2=[];             %storing detected event2's time
    INDdet3=[];             %storing detected event3's time
    INDdet4=[];             %storing detected event4's time
    
%START of MAIN LOOP********************************************************    
        for ii=max([lm1,lm2,lm3,lm4])+1:lu
            %REAL-TIME UPDATE
                ymfilt1(ii)=1/lm1*(((mfiltd1*uax(ii-lm1+1:ii)')));
                ymfilt2(ii)=1/lm2*(((mfiltd2*uax(ii-lm2+1:ii)')));
                ymfilt3(ii)=1/lm3*(((mfiltd3*uay(ii-lm3+1:ii)')));
                ymfilt4(ii)=1/lm4*(((mfiltd4*uay(ii-lm4+1:ii)')));
            
            %REAL-TIME DETECTION    
            if ymfilt1(ii)>THdet1 & ymfilt1(ii-1)<=THdet1
                INDdet1=[INDdet1,ii];   %detected event1
            end
            if ymfilt2(ii)>THdet2 & ymfilt2(ii-1)<=THdet2
                INDdet2=[INDdet2,ii];   %detected event2
            end
            if ymfilt3(ii)>THdet3 & ymfilt3(ii-1)<=THdet3
                INDdet3=[INDdet3,ii];   %detected event3
            end 
            if ymfilt4(ii)>THdet4 & ymfilt4(ii-1)<=THdet4
                INDdet4=[INDdet4,ii];   %detected event4
            end 
        end  
%END of MAIN LOOP**********************************************************

%**************************************************************************    
%END REAL-TIME DETECTION AND CLASSIFICATION ALG.***************************
%**************************************************************************
        
%**************************************************************************    
%START post-processing*****************************************************
%**************************************************************************
        ymfilt1(ymfilt1<0)=0;   %eliminate negative correlation with matched filter1
        ymfilt2(ymfilt2<0)=0;   %eliminate negative correlation with matched filter2
        ymfilt3(ymfilt3<0)=0;   %eliminate negative correlation with matched filter3
        ymfilt4(ymfilt4<0)=0;   %eliminate negative correlation with matched filter4
          
%plotting******************************************************************                 
    figure(1) 
        plot(t*1e0,ax,'r--'); hold on;
        plot(tu*1e0,uax,'b-'); hold on;
        yL = get(gca,'YLim');
        dyL=max(yL)-min(yL);
        ym=max(yL)-0.05*dyL;
        for ii=1:le
            switch e(ii)
                case 0
%                plot(tu(INDte(ii))*1e0,ym,...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);hold on;
                    text(tu(INDte(ii))*1e0,ym,'0','color','b')
                    xline(tu(INDte(ii)),'b--');     %drawing vertical line
                case 1
%                plot(tu(INDte(ii))*1e0,ym,...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);hold on;
                    text(tu(INDte(ii))*1e0,ym,'1','color','k')
                    xline(tu(INDte(ii)),'k--');     %drawing vertical line
                case 2
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','w','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'2','color','m')
                    xline(tu(INDte(ii)),'m--');     %drawing vertical line
                case 3
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','r','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'3','color','r')
                    xline(tu(INDte(ii)),'r--');     %drawing vertical line
                case 4
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','g','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'4','color','g')
                    xline(tu(INDte(ii)),'g--');     %drawing vertical line
            end
        end
        title('Time Domain Dominant (x-Component) of Acceleration & Events'); 
        xlabel('Time in sec');
        ylabel('Magnitude');
        legend('Original','Interpolated','Location','SouthWest');  
        grid on;
    hold off;    
        
    figure(2)
        plot(dts*(1:lm1),mfiltd1,'k-');hold on;
        plot(dts*(1:lm2),mfiltd2,'m-');hold on;
        plot(dts*(1:lm3),mfiltd3,'r-');hold on;
        plot(dts*(1:lm4),mfiltd4,'g-');hold on;
        title('Matched Filters'); 
        xlabel('Time in sec');
        ylabel('Magnitude');
        legend('1-accelerate','2-brake','3-swerve left','4=swerve right');     
        grid on;
    hold off;    
        
    figure(3) 
        plot(t*1e0,ax,'r--'); hold on;
        plot(t*1e0,ay,'b--'); hold on;
        plot(t*1e0,az,'k--'); hold on;
        yL = get(gca,'YLim');
        dyL=max(yL)-min(yL);
        ym=max(yL)-0.05*dyL;
        for ii=1:le
            switch e(ii)
                case 0
%                plot(tu(INDte(ii))*1e0,ym,...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);hold on;
                    text(tu(INDte(ii))*1e0,ym,'0','color','b')
                    xline(tu(INDte(ii)),'b--');     %drawing vertical line
                case 1
%                plot(tu(INDte(ii))*1e0,ym,...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);hold on;
                    text(tu(INDte(ii))*1e0,ym,'1','color','k')
                    xline(tu(INDte(ii)),'k--');     %drawing vertical line
                case 2
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','w','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'2','color','m')
                    xline(tu(INDte(ii)),'m--');     %drawing vertical line
                case 3
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','r','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'3','color','r')
                    xline(tu(INDte(ii)),'r--');     %drawing vertical line
                case 4
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','g','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'4','color','g')
                    xline(tu(INDte(ii)),'g--');     %drawing vertical line
            end
        end
        title('Time Domain Acceleration (x,y,z) & Events'); 
        xlabel('Time in sec');
        ylabel('Magnitude');
        legend('x','y','z');  
        grid on;
    hold off;   
    
    figure(4) 
        plot(tu*1e0,ymfilt1,'k-','Linewidth',3); hold on;
        plot(tu*1e0,THdet1*ones(1,lu),'k--','LineWidth',1); hold on;
        plot(tu(INDdet1),ymfilt1(INDdet1),'kd','MarkerSize',10,'MarkerFaceColor','y');hold on;
        plot(tu*1e0,ymfilt2,'m-','Linewidth',3); hold on;
        plot(tu*1e0,THdet2*ones(1,lu),'m--','LineWidth',1); hold on;
        plot(tu(INDdet2),ymfilt2(INDdet2),'md','MarkerSize',10,'MarkerFaceColor','y');hold on;
        plot(tu*1e0,ymfilt3,'r-','Linewidth',3); hold on;
        plot(tu*1e0,THdet3*ones(1,lu),'r--','LineWidth',1); hold on;
        plot(tu(INDdet3),ymfilt3(INDdet3),'rd','MarkerSize',10,'MarkerFaceColor','y');hold on;
        plot(tu*1e0,ymfilt4,'g-','Linewidth',3); hold on;
        plot(tu*1e0,THdet4*ones(1,lu),'g--','LineWidth',1); hold on;
        plot(tu(INDdet4),ymfilt4(INDdet4),'gd','MarkerSize',10,'MarkerFaceColor','y');hold on;
        yL = get(gca,'YLim');
        dyL=max(yL)-min(yL);
        ym=max(yL)-0.05*dyL;
%        ylim([0 1.1]);
        for ii=1:le
            switch e(ii)
                case 0
%                plot(tu(INDte(ii))*1e0,ym,...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);hold on;
                    text(tu(INDte(ii))*1e0,ym,'0','color','b')
                    xline(tu(INDte(ii)),'b--');     %drawing vertical line
                case 1
%                plot(tu(INDte(ii))*1e0,ym,...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);hold on;
                    text(tu(INDte(ii))*1e0,ym,'1','color','k')
                    xline(tu(INDte(ii)),'k--');     %drawing vertical line
                case 2
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','w','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'2','color','m')
                    xline(tu(INDte(ii)),'m--');     %drawing vertical line
                case 3
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','r','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'3','color','r')
                    xline(tu(INDte(ii)),'r--');     %drawing vertical line
                case 4
%                plot(tu(INDte(ii))*1e0,uax(INDte(ii)),...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','g','MarkerSize',12);hold on;
                    text(tu(INDte(ii))*1e0,ym,'4','color','g')
                    xline(tu(INDte(ii)),'g--');     %drawing vertical line
            end
        end
        title('Matched Filter Detection of Events'); 
        xlabel('Time in sec');
        ylabel('Magnitude');
%        legend('Output1','Detection Treshold1','Detected E1','Output2','Detection Treshold2',...
%               'Detected E2','Location','SouthWest');  
        grid on;
    hold off;    
    
    figure(5) 
%        plot(tu*1e0,ymfilt1,'k-','Linewidth',3); hold on;
%        plot(tu*1e0,THdet1*ones(1,lu),'k--','LineWidth',1); hold on;
        plot(tu(INDdet1),ymfilt1(INDdet1)/THdet1,'kd','MarkerSize',10,'MarkerFaceColor','k');hold on;
%        plot(tu*1e0,ymfilt2,'m-','Linewidth',3); hold on;
%        plot(tu*1e0,THdet2*ones(1,lu),'m--','LineWidth',1); hold on;
        plot(tu(INDdet2),2*ymfilt2(INDdet2)/THdet2,'md','MarkerSize',10,'MarkerFaceColor','m');hold on;
%        plot(tu*1e0,ymfilt3,'r-','Linewidth',3); hold on;
%        plot(tu*1e0,THdet3*ones(1,lu),'r--','LineWidth',1); hold on;
        plot(tu(INDdet3),3*ymfilt3(INDdet3)/THdet3,'rd','MarkerSize',10,'MarkerFaceColor','r');hold on;
%        plot(tu*1e0,ymfilt4,'g-','Linewidth',3); hold on;
%        plot(tu*1e0,THdet4*ones(1,lu),'g--','LineWidth',1); hold on;
        plot(tu(INDdet4),4*ymfilt4(INDdet4)/THdet4,'gd','MarkerSize',10,'MarkerFaceColor','g');hold on;
        yL = get(gca,'YLim');
        dyL=max(yL)-min(yL);
        ym=max(yL)-0.05*dyL;
        ylim([0 5]);
        for ii=1:le
            switch e(ii)
                case 0
%                plot(tu(INDte(ii))*1e0,ym,...
%                'ko','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);hold on;
%                    text(tu(INDte(ii))*1e0,ym,'0','color','b')
%                    xline(tu(INDte(ii)),'b--');     %drawing vertical line
                case 1
                plot(tu(INDte(ii))*1e0+3,4.5,...
                'k^','MarkerEdgeColor','k','MarkerFaceColor','k','MarkerSize',12);hold on;
%                    text(tu(INDte(ii))*1e0,ym,'1','color','k')
                    xline(tu(INDte(ii))+3,'k--');     %drawing vertical line
                case 2
                plot(tu(INDte(ii))*1e0+3,4.5,...
                'm^','MarkerEdgeColor','m','MarkerFaceColor','m','MarkerSize',12);hold on;
%                    text(tu(INDte(ii))*1e0,ym,'2','color','m')
                    xline(tu(INDte(ii))+3,'m--');     %drawing vertical line
                case 3
                plot(tu(INDte(ii))*1e0+3,4.5,...
                'r^','MarkerEdgeColor','r','MarkerFaceColor','r','MarkerSize',12);hold on;
%                    text(tu(INDte(ii))*1e0,ym,'3','color','r')
                    xline(tu(INDte(ii))+3,'r--');     %drawing vertical line
                case 4
                plot(tu(INDte(ii))*1e0+3,4.5,...
                'g^','MarkerEdgeColor','g','MarkerFaceColor','g','MarkerSize',12);hold on;
%                    text(tu(INDte(ii))*1e0,ym,'4','color','g')
                    xline(tu(INDte(ii))+3,'g--');     %drawing vertical line
            end
        end
        title('Matched Filter Detection of Events'); 
        xlabel('Time in sec');
        ylabel('Magnitude');
        legend('Accelerate','Brake','Swerve Left','Swerve Right','Location','SouthWest');  
        grid on;
    hold off;    
    
%printing******************************************************************
        str = ['Detection Threshold Value for e1=', num2str(THdet1)];
            disp(str); 
        str = ['Detection Threshold Value for e2=', num2str(THdet2)];
            disp(str); 
        str = ['Detection Threshold Value for e3=', num2str(THdet3)];
            disp(str);  
        str = ['Detection Threshold Value for e4=', num2str(THdet4)];
            disp(str);      
        str = ['Input Sample Rate(Hz)           =', num2str(fs)];
            disp(str); 
        str =' '; disp(str);    %print one empty line    
        
%**************************************************************************    
%END post-processing*******************************************************
%**************************************************************************       
    
    
   