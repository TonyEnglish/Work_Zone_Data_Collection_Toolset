//
//	************************ R S Z W / L C ****************************
//	
//	JavaScript functions uses Google map to:
//		1. 	Overlay vehicle path data collected for constructing waypoints (node points) representing all 
//			approach and work zone lanes 
//		2.  Overlay constructed approach and work zone lanes waypoints using different icons
//		3.	Draw filled rectangular bounding box between each waypoint (node) segment
//		4.	Replay collected data including test vehicle movement from the tes.
//
//
//	Data arrays used by different function are created in pyhton from vehicle path data 
//
//	Developed by J. Parikh @ CAMP for the V2I Safety Application Project(CAMP)
//	
//	Initial version - August 2017		Version 1.0
//	Revised data structure - Sept. 2017	Version 1.1
//	Revised version - November 25, 2017 Version 1.2
//
//
//
//****	GLOBAL VARIABLES included from *.js file generated in python from processing vehicle path data...	****
//
//		Following global variables are included by *.js file generated in python...
//
//	    refPoint			[lat,lon,elev]
//	    noLanes
// 		mappedLaneNo
//		laneStat			list of lane status to indicate lane open/close with array index pointing to mapData array 
//							[idx,lane #, 0/1, offset in meters from ref. pt]...
//		wpStat				list of workers present status to indicate workers present zone with array index pointing 
//							to mapData array [idx,0/1, offset in meters from ref. pt]...
//		laneWidth			in meters
//		mapData				vehicle path data [speed,lat,lon,elev,vehicle heading]
//		appMapData			array of constructed waypoints for each approach lane [lat,lon,elev,0/1]... + heading,WP flag
//		wzMapData			array of constructed waypoints for each work zone lane [lat,lon,elev,0/1]... + heading,WP flag
//
//*******************************
//	
//****	GLOBAL VARIABLES   ****
//
//****	
//		Canvas and Google map options... 
//****
		
		var rszwMap;											//Map object
		var myMapOptions;										//map options
		
//
//		WZ Map Overlay flag..
//
		wzMapOverlayDone = false;								//overlay not done... 			
				
		if (refPoint[0] == 0 && refPoint[1] == 0)
		{
			refPoint = [mapData[0][1], mapData[0][2], mapData[0][3]];
		}
//****		
//		Variables are used for replaying test data and to animate vehicle movement
//**** 
		var myPrevPos, prevPosMarker, currPosMarker;			//previous position and marker							
		var prevVehIdx; 										//Veh heading index	
		var carMarker = [];										//Array of car icon objects
//****
//		Variables to hold description of each data point and dot icon for conducted 
//		application test data for display using clickable infoWindow
//
//		Following testData array is no longer used for WZ Map Display...
//
//				REMOVED FROM THIS SOURCE...
//
//****
	//	var testDataDesc = new Array(testData.length);			//each data point display string
	//	var testDataIcon = new Array(testData.length);			//dot array for each data point

//****
//		Variables to hold description of each data points for approach and WZ lanes waypoints (nodes)
//****		
		var mapDataDesc = new Array();							//description for displayed dot for collected map data
		var appDataDesc = new Array();							//description for displayed dot for constructed approach lane map data
		var wzDataDesc  = new Array();							//description for displayed dot for constructed approach lane map data		
		var lnDataDesc  = new Array();							//description for displayed icon for lane status marked in veh path data
		
//****
//		Variables to indicate start and end of test data markers
//		Global variable i must be used with care. Must be reset prior to using it.
//**** 
		var i,dataStart, dataEnd;
				
//****
//		Function to initialize 
//		1. collected vehicle path data
//		2. constructed waypoints for approach lane(s)
//		3. constructed waypoints for WZ lane(s) including lane closure(s)
//		
//		for display using clickable infoWindow
//****

		function initDisplayWZMap()									//Function to initialize map and waypoint(node) data points 
		{
//****
//			Collected vehicle path data...
//****			
			var vSspeed, vSpeedMPH;									//local temp variables 
			var fontSize = "<font size=\"2\">";						//set small font size for infoWindow display
		
			for (i = 0; i < mapData.length; i++)
			{
				vSpeed = String(mapData[i][0].toFixed(1))+ " m/s";
				vSpeedMPH = " ("+String((mapData[i][0]*2.23694).toFixed(1))+" mph)";
				mapDataDesc[i] = fontSize+"<b>Data Point#: </b>"+String(i)+";<b> Veh Speed: </b>"+vSpeed+vSpeedMPH+";<b> Lat/Lon/Elev: </b>"+String(mapData[i][1])+", "+String(mapData[i][2])+", ";
				mapDataDesc[i] = mapDataDesc[i]+String(mapData[i][3].toFixed(0))+";<b> Heading: </b>"+String(mapData[i][4].toFixed(2));
			}
//****
//			Constructed waypoints data for each approach lane...
//****
			i = 0;
			for (ln = 0; ln < noLanes; ln++)						//lanewise desc and icon array construction...
			{
				for (ap = 0; ap < appMapData.length; ap++)	
				{
					appLLE = String(appMapData[ap][ln*4+0])+", "+String(appMapData[ap][ln*4+1])+", "+String(appMapData[ap][ln*4+2]);
					appLLE = ";<b> Lat/Lon/Elev: </b>" + appLLE;
					appDataDesc[i] = fontSize+"<b>Lane/Node: </b>"+String(ln+1)+"/"+String(ap+1)+appLLE;
					i++;
				}
			}
//****
//			Constructed waypoints data for each WZ lane...
//****			
			i = 0;
			for (ln = 0; ln < noLanes; ln++)						//lanewise description and icon array construction...
			{
				for (wz = 0; wz < wzMapData.length; wz++)			//for each lane, do all wz map waypoints	
				{
//
//					Construct lcStat description string...
//			
					lcStat = ", LO";															//Lane open at this node	
					if (wzMapData[wz][ln*4+3] 		== 1)	{lcStat = ", LC";}					//Lane closed at this node
					if (wzMapData[wz][noLanes*4+1] 	== 1)	{lcStat = lcStat+"+WP";}			//Workers present at this node
			//		lcStat = "<b>"+lcStat+": </b>"
					lcStat = "<b>"+"Lane/Node: </b>"+String(ln+1)+"/"+String(wz+1)+lcStat;
//
//					Construct node's Lat,Lon,Elev description string...
//			
					wzLLE = String(wzMapData[wz][ln*4+0])+", "+String(wzMapData[wz][ln*4+1])+", "+String(wzMapData[wz][ln*4+2]);
					wzLLE = ";<b> Lat/Lon/Elev: </b>" + wzLLE;
					wzDataDesc[i] = fontSize+lcStat+wzLLE;
					i++;
				}	
			}			
		}						//end of function initDiaplayWZMap

//		
//**	initialize the display string and associated dot icons for each of the test data point from
//		running the RSZW/LC application
//
//**	initDiaplayWZTest Function is NOT USED in this WZ Map Visualization...
//**			REMOVED FROM THIS SOURCE...
//**
//
////	-----------------------------------------------------------------------------------------------		
//
//		Alternate function to construct infowindow for clickable data point description...	
//
//**	Following Function is NOT USED for WZ Visualization...
//		
		
		function showMapTestDotInfo(dotPos,dotIcon,dotDesc) 
		{
			var infoWindow = new google.maps.InfoWindow ();
			dotMarker = new google.maps.Marker (
				{	
					position: dotPos,
					map: rszwMap,
					icon: dotIcon
				}
			);
//
//			Set Listener for information window. Onclick pop-up display string
//
			google.maps.event.addListener(dotMarker, 'click', (function(dotMarker) 
			{
				return function()
				{
					infoWindow.setContent(dotDesc);
					infoWindow.open(rszwMap,dotMarker);
				}
			})
				(dotMarker));	
		}	
									

//******
//		Following function can be used to display text on a canvas...
//
//		***** NOT USED ***** in this program; Alternate method is used...								
//
//******
									
		function showWZInfo()
		{	
			var wzInfo = document.getElementById("wzInfo_canvas");
			var infoContext = wzInfo.getContext("2d");
			var nodesPerLane = [0,0];
			
			nodesPerLane = [msgSegList[1][2], msgSegList[msgSegList.length-1][2]];
		
			infoContext.clearRect(0,0,1200,500);
			
			infoContext.fillStyle = 'royalblue';
			infoContext.font = '12px sans-serif';
			infoContext.textBaseline = 'bottom';
			yPos = 3;
			infoContext.fillText("Work Zone: "+wzDesc, 10, yPos+15);
			infoContext.fillText("Map Created: "+wzMapDate, 10, yPos+30);
			infoContext.fillText("WZ Ref. Point at: "+String(refPoint[0]), 10, yPos+45);
			infoContext.fillText("# of Lanes in WZ: "+String(noLanes), 10, yPos+60);
			infoContext.fillText("Vehicle path data lane: "+String(mappedLaneNo), 10, yPos+75);
			infoContext.fillText("Mapped nodes per Approach / WZ lanes: "+String(nodesPerLane[0])+" / "+String(nodesPerLane[1]), 10, yPos+90);	
			
			var legendImg = new Image();
			legendImg.onload = function () 
			{
			//	infoContext.drawImage(legendImg, 600,3);
			}			
		}
								
//***************************************************
//		On load from the html file, start here...
//***************************************************

		function startHere()
		{
//
//			Built display dot icon and display string for each data point for Map and Test Data...
//			
			initDisplayWZMap();											//Map data points
//**		initDisplayWZTest();  *** NOT NEEDED FOR WZ VISUALIZATION, FUNCTION REMOVED FROM THIS SOURCE ***	//Test data points		
								
			i = dataStart;												//start at first non-zero vehicle speed					
	
//*******************************************************************************					
//			Start displaying stuff...		
//			Setup google map parameters... 
//*******************************************************************************
					
			var myMapOptions =															//gMap options... 			
				{	
					zoom: 20,															//Works only if fitBounds below is commented out...
					center: new google.maps.LatLng(refPoint[1],refPoint[2]),			//Reference Point...
					// center: new google.maps.LatLng(mapData[0][1], mapData[0][2]),	//First map data point
					mapTypeId: google.maps.MapTypeId.HYBRID,							//Satellite + Street names
					mapTypeControl: true,
					zoomControl: true,
					scaleControl: true,
					mapTypeControl: true,
					streetViewControl: true,
					rotateControl: true,
					fullscreenControl: true
				};	
				
			rszwMap = new google.maps.Map(document.getElementById("map_canvas"), myMapOptions);	
			rszwMap.setTilt(0);										//set map tilt to 0 or 45 degrees
			
//****
//			Local variables for ref point and other icons
//****		
			var refPointIcon   	= 'Icons\\refPoint3Green.png';			//ref point icon
			var mapDataPtIcon  	= 'Icons\\vehPath2.png';				//vehicle path data point icon
			
			var laneOpenIcon	= [['Icons\\lane1OpenPoint.png', 'Icons\\lane2OpenPoint.png',
									'Icons\\lane3OpenPoint.png', 'Icons\\lane4OpenPoint.png',
									'Icons\\lane5OpenPoint.png', 'Icons\\lane6OpenPoint.png',
									'Icons\\lane7OpenPoint.png', 'Icons\\lane8OpenPoint.png']];
			
			var laneClosedIcon	= [['Icons\\lane1ClosedPointO.png', 'Icons\\lane2ClosedPointO.png',
									'Icons\\lane3ClosedPointO.png', 'Icons\\lane4ClosedPointO.png',						
									'Icons\\lane5ClosedPointO.png', 'Icons\\lane6ClosedPointO.png',						
									'Icons\\lane7ClosedPointO.png', 'Icons\\lane8ClosedPointO.png']];						
			
			var wpPointIcon		= [['Icons\\wpPointO.png', 'Icons\\wnpPoint.png']];
											
//****			
//			place collected vehicle path data points with purple dots on google map... 
//			Call function to associate clickable info.window for each data point...
//****			
			for (md = 0; md < mapDataDesc.length; md++)
			{
				dotLoc = new google.maps.LatLng(mapData[md][1], mapData[md][2]);
				showDotInfo(dotLoc,mapDataPtIcon,mapDataDesc[md]);	//function to show placed dot icon and assocaited description		
		//		md = md + 2;										//skip points for display 
			}			

//****
//			Place the reference point on map, associate current data point,lat,lon,elev for infoWindow
//****		
			var refPointDesc = "<b>Ref. Pt. @ Data Pt.: </b>"+String(refPoint[0])+",<b> Lat/Lon/Elev: </b>"+String(refPoint[1])+", "+String(refPoint[2])+", "+String(refPoint[3]);
			var refPointLoc = new google.maps.LatLng(refPoint[1]+0.000005,refPoint[2]+0.000005);	//Show reference point, slightly offset

			showDotInfo(refPointLoc,refPointIcon,refPointDesc);		//show reference point with description
			
			rszwMap.setCenter(refPointLoc);							//Center map to reference point		
						
//********************************************************************
//			Start displaying WZ parameters, lane and workers presence status stuff...		
//			Build txt string with html tags to display WZ information Msg + Legends 
//********************************************************************			

			var nodesPerLane = [0,0];
			var txt = "";
						
			nodesPerLane = [msgSegList[1][2], msgSegList[msgSegList.length-1][2]];			
//
//		Build the complete text string describing WZ parameters...
//		Complete text is displayed later after building lane status and workers presence status... 	
//			
			txt = "<center><b><font size='3'>Mapped Work Zone</b></font></br></center>";
			txt = txt + "<Center><b><font color='blue'>"+wzDesc+"</b></font><hr></center>";
			txt = txt + "Map Created: <b>"+wzMapDate+"</b></br>";
			
//			WZ length - in the RSZW_MAP_jsData.js data file for map generated prior to Jan. 2019
//				does not have wzLength variable. To avoid error following is added... Jan. 10, 2019
//				 			
			if (typeof wzLength !== "undefined")
			{
				txt = txt + "Mapped WZ Length (meters):</br>";
				txt = txt + "&nbsp;&nbsp;App: <b>"+String(wzLength[0])+"</b> + WZ: <b>"+String(wzLength[1])+"</b> = <b>"
						+  String(wzLength[0]+wzLength[1])+"</b></br>";
			}
			
			txt = txt + "Start of WZ @ Data Point: <b>"+String(refPoint[0])+";</b></br> &nbsp;&nbsp;@ Lat/Lon: <b>"
					  +  String(refPoint[1])+", "+String(refPoint[2])+"</b></br>";
			txt = txt + "# of Lanes in WZ: <b>"+String(noLanes)+"</b></br>";
			txt = txt + "Vehicle Path Data Lane: <b>"+String(mappedLaneNo)+"</b></br>";
			txt = txt + "Nodes Per Approach/WZ Lanes: <b>"+String(nodesPerLane[0])+"/"+String(nodesPerLane[1])+"</b></br>";
			txt = txt + "<hr><b><center>Start/End of Lane Closures</b></center>";
			
//****
//			Overlay lane status (close/open) marked during vehicle path data collection...
//****			
			for (ls = 1; ls < laneStat.length; ls++)
			{
				dataPt = laneStat[ls][0];
								
				if (laneStat[ls][2] == 1)
				{
					lStat = "<font color='red'>Start of Lane #";
					lsIcon = laneClosedIcon[0][laneStat[ls][1]-1];
					txt = txt + "<font color='red'>&emsp;Start of Lane #"+String(laneStat[ls][1])+" Closure @: "+String(dataPt)+"</font>";			//Text for Start of LC
				}
				
				if (laneStat[ls][2] == 0)	
				{
					lStat = "<font color='green'>End of Lane #"; 
					lsIcon = laneOpenIcon[0][laneStat[ls][1]-1];
					txt = txt + "<font color='green'>&emsp;End of Lane #"+String(laneStat[ls][1])+" Closure @: "+String(dataPt)+"</font>";	//Text for End of LC
				}
				
//
//				Place the lane status icon w/ description... 
//			
				laneStatDesc = "<b>Data Point#: "+String(dataPt)+", "+lStat+String(laneStat[ls][1])+" Closure<b>";
				dotLoc = new google.maps.LatLng(mapData[dataPt+0][1], mapData[dataPt+0][2]);
				showDotInfo(dotLoc,lsIcon,laneStatDesc);					//function to show placed dot icon and associated description									
//
//				Add horizontal line...
//								
				txt = txt + "</br>";
			}			
							
//**********
//			Overlay workers present zone status (start/end) marked during vehicle path data collection...
//**********		

			txt = txt + "<hr><b><center>Start/End of Workers Presence</b></center>";			//WP/WnP text for display...
					
			for (wp = 0; wp < wpStat.length; wp++)
			{
				dataPt = wpStat[wp][0];
				
				if (wpStat[wp][1] == 1)
				{
					wStat = "<font color='red'>Start of Workers Presence";
					wpIcon = wpPointIcon[0][0];
					txt = txt + "<font color='red'>&emsp;&emsp;Start @: "+String(dataPt)+"</font>";			//Text for Start of WP
				}
				
				if (wpStat[wp][1] == 0)	
				{
					wStat = "<font color='green'>End of Workers Presence"; 
					wpIcon = wpPointIcon[0][1];
					txt = txt + "<font color='green'>&emsp;&emsp; End @: "+String(dataPt)+"</font></br>";	//Text for End of WP
				}				
//
//				Overlay WP marker...
//
				wpStatDesc = "<b>Data Point#: "+String(dataPt)+ ", " + wStat+"<b>";			
				dotLoc = new google.maps.LatLng(mapData[dataPt+0][1], mapData[dataPt+0][2]);
				showDotInfo(dotLoc,wpIcon,wpStatDesc);			//function to show placed dot icon and assocaited description
			}			
//
//			Add horizontal line...
//		
			txt = txt + "<hr>";			
//
//			Display completed text...
//
			txt = txt + "<button class='overlay_btn' onclick='displayMapNodes_drawRectBB();'>Overlay WZ Map</button>";
			txt = txt + "</br><p>";
			txt = txt + "<img src = './Icons/Legends-RSZW8.png' class='wzLegends'>";			
//		
//		The following is a fancy way to show larger legend image using onmouseover and onmouseout...
//		... NOT USED... It does not pop-up on the map, but works great on wzInfo_text section
///			
		
	////		txt = txt + "<img onmouseover='bigLegend(this)' onmouseout='smallLegend(this)' border='0'		\
 	////				      src='./Icons/Legends-RSZW5.png' alt='Legends' width='128' style='left:50px'>";
			
			document.getElementById('wzInfo_text').innerHTML = txt;
									
		}															//end of startHere()	

		function bigLegend(x)
		{
			x.style.width = "300px";
			x.style.left = "1px";
			x.style.zIndex="1"; 	
		}
		
		function smallLegend(x)
		{
			x.style.width = "128px";
			x.style.left = "50px";
		}
		
//************************************************************************************************************************
//
//		Following function is invoked by clicking a button from the html file (same as startHere() function)...	
//
//************************************************************************************************************************
//****
//		Function to place constructed map node points for approach lanes and WZ lane
//		Also, draw rectangle bounding box between the node points
//
//****

		function displayMapNodes_drawRectBB()
		{
//****
//			Local variables...
//****			
			var appDataPtIcon = 'Icons\\approachPoint.png';
			var wzDataPtIcon  = 'Icons\\wzPoint2.png';
			var wzLanOpenIcon = 'Icons\\wzLaneOpen3.png';
			var wzLCPtIcon    = 'Icons\\orangeBarrelSmall1.png';
			var wzWPPtIcon    = 'Icons\\wzWorkers4.png';
			var dotLoc, dotLoc1, wpIconLoc;
			
			
			var halfLWApp = (laneWidth + lanePadApp)/2;			//data point is in middle of the lane + approach lane padding
			var headLoc = noLanes*4;							//for each lane, 4 columns (lon,lat,elev,0/1)
						
			i = 0;	
			///console.log("No Lanes = ", noLanes, refPoint);
			
			for (ln = 0; ln < noLanes; ln++)
			{
				for (ap = 0; ap < appMapData.length; ap++)
				{
					dotLoc = new google.maps.LatLng(appMapData[ap][ln*4+0], appMapData[ap][ln*4+1]);
					showDotInfo(dotLoc,appDataPtIcon,appDataDesc[i]);
					 		
					if (mappedLaneNo == ln+1 && ap < appMapData.length-1)
					{			
						dotLoc1 = new google.maps.LatLng(appMapData[ap+1][ln*4+0],appMapData[ap+1][ln*4+1]);
//****
//						Draw a rectangular box around the collected map data points bet two constructed APP points
//						equal to the laneWidth+lanePad to see how many points are outside the box. 
//						This visualization provides clue on a curved lane the dist between points and need for   
// 						creating dynamic distance between map points for approach and wz lanes...
//**** 		
						drawRectBB (dotLoc, dotLoc1, halfLWApp, appMapData[ap+0][headLoc], appMapData[ap+1][headLoc], 'Green');
					}
					i++;
				}
			}

//****			
//			place constructed WZ lane map data points on the map... 
//			Call function to associate clickable info.window for each data point...
//****
			var halfLWWZ = (laneWidth + lanePadWZ)/2;					//data point is in middle of the lane + WZ lane padding
			var wzIcon;	
			var spherical = google.maps.geometry.spherical;
			
			i = 0;
			for (ln = 0; ln < noLanes; ln++)
			{
				for (wz = 0; wz < wzMapData.length; wz++)
				{
					wzIcon = wzLanOpenIcon;												//wz Icon
					if (wzMapData[wz][ln*4+3] == 1)	{wzIcon = wzLCPtIcon;}				//LC at this node		
//****
//					overlay icon for wz node on g. map...
//***	
					dotLoc = new google.maps.LatLng(wzMapData[wz][ln*4+0],wzMapData[wz][ln*4+1]);
					showDotInfo(dotLoc,wzIcon,wzDataDesc[i]);
//****
//					For workers present, the icon will be displayed outside the last (right most) lane only 
//					and not on each lane...
//					added on Dec. 1, 2017
//****					
					if (wzMapData[wz][noLanes*4+1] 	== 1) 								//Workers present at this node
					{
						if (ln == noLanes-1)
						{
//****			
//							Construct coords to overlay workers present icon outside the last lane...			
//****
							wpIconLoc = spherical.computeOffset(dotLoc, halfLWWZ*2, wzMapData[wz+0][headLoc]+90.0);
						
//							wpIconLoc = new google.maps.LatLng(wzMapData[wz][ln*4+0],wzMapData[wz][ln*4+1]);  outside the last lane...
//							showDotInfo(wpIconLoc,wzWPPtIcon,wzDataDesc[i]);
							showDotInfo(wpIconLoc,wzWPPtIcon,"Workers Present...");		//Clickable description for infoWindow...
						}
					}
//****
//					Draw a rectangular box on the collected map data lane points bet two points (WZ map point) 
//					equal to the laneWidth to see how many points are outside the box. This visualization provides clue 
//					of curved lane and how to create dynamic distance between map points for approach and wz lanes...
//**** 		
					if (mappedLaneNo == ln+1 && wz < wzMapData.length-1)
					{			
						dotLoc1 = new google.maps.LatLng(wzMapData[wz+1][ln*4+0],wzMapData[wz+1][ln*4+1]);
//****
//						Draw a rectangular box around the collected map data lane points bet two constructed WZ points
//						equal to the laneWidth+lanePad to see how many points are outside the box. 
//						This visualization provides clue on a curved lane the dist between points and need for   
// 						creating dynamic distance between map points for approach and wz lanes...
//**** 		
						drawRectBB (dotLoc, dotLoc1, halfLWWZ, wzMapData[wz+0][headLoc], wzMapData[wz+1][headLoc], 'Blue');
					}
					i++;
				}
			}
//
//			Disable the button now...	Following doesn't work, may be need to make the button global...
//			Will do some other time...
//			
//			document.getElementsByClassName('overlay_btn').disabled = true;
		}										//end of displayMapNodes_drawBB
			
//****	
//		Function below draws a rectangular bounding box on the collected vehicle path lane data points bet two constructed
//		waypoints (node points). The bounding box is equal to the laneWidth to see how many vehicle path points are falling 
//		outside the box that indicates that the map matching would fail in that area and the constructed waypoints (node points)
//		are incorrect. This visualization is particularly handy to see how the waypoints are selected by the python s/w that 
//		generated the waypoints (node points) on a curved lane...
//**** 				
		
		function drawRectBB (dotLoc0, dotLoc1, dist, head0, head1, fColor)
		{
			var spherical = google.maps.geometry.spherical;
			var tLeft, tRight, bRight, bLeft;
//			
//			Construct coords for four corners			
//
			tLeft  = spherical.computeOffset(dotLoc0, dist, head0-90.0);				
			tRight = spherical.computeOffset(dotLoc0, dist, head0+90.0);
			bRight = spherical.computeOffset(dotLoc1, dist, head1+90.0);
			bLeft  = spherical.computeOffset(dotLoc1, dist, head1-90.0);
//						
// 			Draw the rectangle polygon.
//
			var rectCoords = [tLeft,tRight,bRight,bLeft];
			var mapRect = new google.maps.Polygon({
				paths: rectCoords,
				strokeColor: '#FF0000',
				strokeOpacity: 0.8,
				strokeWeight: 1,
				fillColor: fColor,
				fillOpacity: 0.40		
				});	
			mapRect.setMap(rszwMap)		
		}										//end of drawRectBB
		
						
//  *******************************************************************
//
//		Function testDrive() to show test car on google map
//		This function is invoked from button click on the visualization screen 
//		THIS FUNCTION IS NO LONGER USED IN WZ MAP VISUALIZATION - REMOVED... 
//
//  *******************************************************************
			
//
//		****	function showCurrPos (newPos, head)...	NOT USED, REMOVED from THIS SOURCE ...****
//			

//
//		Alternate function to construct infowindow for clickable data point description...	
//				
		function showDotInfo(dotPos,dotIcon,dotDesc) 
		{
			var infoWindow = new google.maps.InfoWindow ();

			dotMarker = new google.maps.Marker (
				{	
					position: dotPos,
					map: rszwMap,
					icon: dotIcon,			
				}
			);
//
//			Set listener for information window. Onclick popup display string
//
			google.maps.event.addListener(dotMarker, 'click', (function(dotMarker) 
			{
				return function()
				{
					infoWindow.setContent(dotDesc);
					infoWindow.open(rszwMap,dotMarker);
				}
			})
				(dotMarker));	
		}										//**** End of showCSWdots *****	
		


		
			
