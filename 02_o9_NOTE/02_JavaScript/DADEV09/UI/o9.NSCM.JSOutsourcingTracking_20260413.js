define('o9.NSCM.JSOutsourcingTracking', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const validation = function (props) {
        try{
    
            const queryModule = require('o9/data/query');
            const cellsetModule = require('o9/data/cellset');
    
            props = JSON.parse(props);
    
            Log.Info("-------------props-----------------------" + JSON.stringify(props));
    
            for (var i = 0; i < props.fbValidation.length; i++){
    
                var curr = props.fbValidation[i];
    
                //var query = `Select ([Version].[Version Name].[CurrentWorkingView] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sales Domain].[Sales Lv3 Name].[${curr.fbAP2.Value}] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type].[${curr.fbOutsourcingType.Value}] * [Project].[Project].[${curr.fbProject.Value}] * [ERP Ship to].[ERP Ship to ID].[${curr.fbERPShipTo.Value}] * [Seq].[Seq].[${curr.fbSeq.Value}] * [Seq2].[Seq2].[${curr.fbSeq2.Value}] ) on row, ({Measure.[Out PO Tracking Status_Reason Category], Measure.[Out PO Tracking Status_Partial Qty], Measure.[Out PO Tracking Status_PO Qty]}) on column;`;
                var query = `Select ([Version].[Version Name].[${props.fbVersion}] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type].[${curr.fbOutsourcingType.Value}] * [ERP Ship to].[ERP Ship to ID].[${curr.fbERPShipTo.Value}] * [Seq].[Seq].[${curr.fbSeq.Value}] * [Seq2].[Seq2].[${curr.fbSeq2.Value}] ) on row, ({Measure.[Out PO Tracking Status_Reason Category], Measure.[Out PO Tracking Status_Partial Qty], Measure.[Out PO Tracking Status_PO Qty]}) on column;`;    
                query = cellsetModule.createCellSet(queryModule.select(query));
    
                var reasonCategory = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Reason Category'));
                var partialQty = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Partial Qty'));
                var POQty = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO Qty'));
    
                Log.Info("-------------reasonCategory-----------------------" + reasonCategory);
                Log.Info("-------------partialQty-----------------------" + partialQty);
                Log.Info("-------------POQty-----------------------" + POQty);
    
                if (!reasonCategory) {
                    RuleOutputToUI = {
                        Status: 'Error',
                        Message: 'Please Select “Reason Category"'
                    };
                    return;
                }
    
                if (!partialQty) {
                    RuleOutputToUI = {
                        Status: 'Error',
                        Message: 'Please Input “Partial Qty"'
                    };
                    return;
                }
    
                //var queryPartialPO = `Select ([Version].[Version Name].[CurrentWorkingView] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sales Domain].[Sales Lv3 Name] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type] * [Project].[Project] * [ERP Ship to].[ERP Ship to ID] * [Seq].[Seq] * [Seq2].[Seq2].[${curr.fbSeq2.Value}] ) on row, ({Measure.[Out PO Tracking Status_Reason Category], Measure.[Out PO Tracking Status_Partial Qty], Measure.[Out PO Tracking Status_PO Qty], Measure.[Out PO Tracking Status_DO No]}) on column;`;
                var queryPartialPO = `Select ([Version].[Version Name].[${props.fbVersion}] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type] * [ERP Ship to].[ERP Ship to ID] * [Seq].[Seq] * [Seq2].[Seq2].[${curr.fbSeq2.Value}] ) on row, ({Measure.[Out PO Tracking Status_Reason Category], Measure.[Out PO Tracking Status_Partial Qty], Measure.[Out PO Tracking Status_PO Qty], Measure.[Out PO Tracking Status_DO No]}) on column;`;

                queryPartialPO = cellsetModule.createCellSet(queryModule.select(queryPartialPO));
    
                Log.Info("-------------queryPartialPO-----------------------" + queryPartialPO);
    
    
                var sum = 0;
    
                for(let j=0; j<queryPartialPO.rowCount; j++){
                    var parQty = queryPartialPO.row(j).cell(queryPartialPO.measureColumnIndex('Out PO Tracking Status_Partial Qty'));
                    sum+=parQty;
                }
    
                Log.Info("-------------sum-----------------------" + sum);
    
                if(POQty!=sum){
                    RuleOutputToUI = {
                        Status: 'Error',
                        Message: "Partial PO's sum Qty. should be same with PO's total Qty."
                    };
                    return;
                }
            }
        }
    
    
    
        catch (e) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
            return;
        }
        };

    const AddPartialPO = function (props) {
        try{
    
            const queryModule = require('o9/data/query');
            const cellsetModule = require('o9/data/cellset');
    
            props = JSON.parse(props);
    
            Log.Info("-------------props-----------------------" + JSON.stringify(props));
            
            for (var i = 0; i < props.fbPartialPO.length; i++){
                var curr = props.fbPartialPO[i];
                
                Log.Info("-------------AddPartialPO For curr-----------------------"+JSON.stringify(curr));
                
                
                var query = `Select ([Version].[Version Name].[${props.fbVersion}] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type].[${curr.fbOutsourcingType.Value}] * [ERP Ship to].[ERP Ship to ID].[${curr.fbERPShipTo.Value}] * [Seq].[Seq].[${curr.fbSeq.Value}] * [Seq2].[Seq2].[${curr.fbSeq2.Value}] ) on row, ({Measure.[Out PO Tracking Status_ATA Date], Measure.[Out PO Tracking Status_ATA Week], Measure.[Out PO Tracking Status_ATA Week Date], Measure.[Out PO Tracking Status_ATD Week], Measure.[Out PO Tracking Status_ATD Week Date], Measure.[Out PO Tracking Status_Arrive Port Code], Measure.[Out PO Tracking Status_Arrive Port Name], Measure.[Out PO Tracking Status_BC Date], Measure.[Out PO Tracking Status_BC No], Measure.[Out PO Tracking Status_BL No], Measure.[Out PO Tracking Status_BL Status], Measure.[Out PO Tracking Status_BR Date], Measure.[Out PO Tracking Status_BR No], Measure.[Out PO Tracking Status_CNTR Arrange Request Date], Measure.[Out PO Tracking Status_CNTR Gate Out Ex-fac Date], Measure.[Out PO Tracking Status_Change ETA Date], Measure.[Out PO Tracking Status_Change ETA Date_Prev], Measure.[Out PO Tracking Status_Chk Flag], Measure.[Out PO Tracking Status_Close Time], Measure.[Out PO Tracking Status_Container No], Measure.[Out PO Tracking Status_Container Type], Measure.[Out PO Tracking Status_DO Create Date], Measure.[Out PO Tracking Status_DO Item], Measure.[Out PO Tracking Status_DO No], Measure.[Out PO Tracking Status_DO Qty], Measure.[Out PO Tracking Status_Delivery Status], Measure.[Out PO Tracking Status_Depart Port Code], Measure.[Out PO Tracking Status_Depart Port Name], Measure.[Out PO Tracking Status_Destination], Measure.[Out PO Tracking Status_Document Type], Measure.[Out PO Tracking Status_ETA Week], Measure.[Out PO Tracking Status_ETA Week Date], Measure.[Out PO Tracking Status_ETD Week], Measure.[Out PO Tracking Status_ETD Week Date], Measure.[Out PO Tracking Status_Empty CNTR Gate IN Date], Measure.[Out PO Tracking Status_Forwarder], Measure.[Out PO Tracking Status_GR Date], Measure.[Out PO Tracking Status_GR Qty], Measure.[Out PO Tracking Status_Gate Out Date], Measure.[Out PO Tracking Status_History], Measure.[Out PO Tracking Status_Incoterms], Measure.[Out PO Tracking Status_Incoterms2], Measure.[Out PO Tracking Status_Local Amt], Measure.[Out PO Tracking Status_PO Create Date], Measure.[Out PO Tracking Status_PO ETD Date], Measure.[Out PO Tracking Status_PO ETD First Date], Measure.[Out PO Tracking Status_PO Item], Measure.[Out PO Tracking Status_PO No], Measure.[Out PO Tracking Status_PO Qty], Measure.[Out PO Tracking Status_PO Seq], Measure.[Out PO Tracking Status_Partial Qty], Measure.[Out PO Tracking Status_Partial Qty_Prev], Measure.[Out PO Tracking Status_Planned ETA Date], Measure.[Out PO Tracking Status_Planned ETA Week], Measure.[Out PO Tracking Status_Planned ETD Date], Measure.[Out PO Tracking Status_Planned ETD Date_Prev], Measure.[Out PO Tracking Status_Planned ETD Week], Measure.[Out PO Tracking Status_Production Closing Date], Measure.[Out PO Tracking Status_Production Plan Date], Measure.[Out PO Tracking Status_Production Plan Date_Prev], Measure.[Out PO Tracking Status_Purchase ORG], Measure.[Out PO Tracking Status_RTP(Y/N)], Measure.[Out PO Tracking Status_Reason Category], Measure.[Out PO Tracking Status_Reason Category_Prev], Measure.[Out PO Tracking Status_Reason Detail], Measure.[Out PO Tracking Status_Reason Detail_Prev], Measure.[Out PO Tracking Status_Remain Qty], Measure.[Out PO Tracking Status_SO Date], Measure.[Out PO Tracking Status_SO Item], Measure.[Out PO Tracking Status_SO No], Measure.[Out PO Tracking Status_SR Issue Date], Measure.[Out PO Tracking Status_SR No], Measure.[Out PO Tracking Status_SR Status], Measure.[Out PO Tracking Status_Ship Company Code], Measure.[Out PO Tracking Status_Ship Company Name], Measure.[Out PO Tracking Status_USD Amt], Measure.[Out PO Tracking Status_Update time], Measure.[Out PO Tracking Status_Updated by], Measure.[Out PO Tracking Status_Vendor PO Item], Measure.[Out PO Tracking Status_Vendor PO No], Measure.[Out PO Tracking Status_Vessel Name]}) on column;`;
                
                Log.Info("-------------AddPartialPO query 22222222-----------------------" + query);
                
                query = cellsetModule.createCellSet(queryModule.select(query));
    
                var DONo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_DO No'));
    
                Log.Info("-------------DONo-----------------------" + DONo);
    
                if (DONo) {
                    RuleOutputToUI = {
                        Status: 'Error',
                        Message: 'Unable to add Partial PO.'
                    };
                    return;
                }

                if(DONo){
                    DONo=`"${DONo}"`;
                }
                Log.Info("-------------DONo-----------------------" + DONo);
                
                var delStatus = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Delivery Status'));
                if(delStatus){
                    delStatus=`"${delStatus}"`;
                }
                Log.Info("-------------delStatus-----------------------" + delStatus);

                var PONo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO No'));
                if(PONo){
                    PONo=`"${PONo}"`;
                }
                Log.Info("-------------PONo-----------------------" + PONo);

                var POItem = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO Item'));
                if(POItem){
                    POItem=`"${POItem}"`;
                }
                Log.Info("-------------POItem-----------------------" + POItem);

                var POSeq = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO Seq'));
                Log.Info("-------------POSeq-----------------------" + POSeq);

                var docType = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Document Type'));
                if(docType){
                    docType=`"${docType}"`;
                }
                Log.Info("-------------docType-----------------------" + docType);

                var purORG = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Purchase ORG'));
                if(purORG){
                    purORG=`"${purORG}"`;
                }
                Log.Info("-------------purORG-----------------------" + purORG);

                var createDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO Create Date'));
                if(createDate){
                    createDate=`"${createDate}"`;
                }
                Log.Info("-------------createDate-----------------------" + createDate);

                var POQty = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO Qty'));
                if(POQty){
                    POQty=`"${POQty}"`;
                }
                Log.Info("-------------POQty-----------------------" + POQty);

                var GRQty = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_GR Qty'));
                if(GRQty){
                    GRQty=`"${GRQty}"`;
                }
                Log.Info("-------------GRQty-----------------------" + GRQty);

                var remainQty = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Remain Qty'));
                if(remainQty){
                    remainQty=`"${remainQty}"`;
                }
                Log.Info("-------------remainQty-----------------------" + remainQty);

                var partialQty = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Partial Qty'));
                if(partialQty){
                    partialQty=`"${partialQty}"`;
                }
                Log.Info("-------------partialQty-----------------------" + partialQty);

                var GRDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_GR Date'));
                if(GRDate){
                    GRDate=`"${GRDate}"`;
                }
                Log.Info("-------------GRDate-----------------------" + GRDate);

                var DOQty = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_DO Qty'));
                if(DOQty){
                    DOQty=`"${DOQty}"`;
                }
                Log.Info("-------------DOQty-----------------------" + DOQty);

                var DOcreateDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_DO Create Date'));
                if(DOcreateDate){
                    DOcreateDate=`"${DOcreateDate}"`;
                }
                Log.Info("-------------createDate-----------------------" + DOcreateDate);
                
                var ETDWeek = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ETD Week'));
                if(ETDWeek){
                    ETDWeek=`"${ETDWeek}"`;
                }
                Log.Info("-------------ETDWeek-----------------------" + ETDWeek);

                var ETAWeek = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ETA Week'));
                if(ETAWeek){
                    ETAWeek=`"${ETAWeek}"`;
                }
                Log.Info("-------------ETAWeek-----------------------" + ETAWeek);

                var plannedETDWeek = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Planned ETD Week'));
                if(plannedETDWeek){
                    plannedETDWeek=`"${plannedETDWeek}"`;
                }
                Log.Info("-------------plannedETDWeek-----------------------" + plannedETDWeek);

                var plannedETAWeek = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Planned ETA Week'));
                if(plannedETAWeek){
                    plannedETAWeek=`"${plannedETAWeek}"`;
                }
                Log.Info("-------------plannedETAWeek-----------------------" + plannedETAWeek);

                var ATDWeek = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ATD Week'));
                if(ATDWeek){
                    ATDWeek=`"${ATDWeek}"`;
                }
                Log.Info("-------------ATDWeek-----------------------" + ATDWeek);

                var ATAWeek = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ATA Week'));
                if(ATAWeek){
                    ATAWeek=`"${ATAWeek}"`;
                }
                Log.Info("-------------ATAWeek-----------------------" + ATAWeek);

                var vendorPONo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Vendor PO No'));
                if(vendorPONo){
                    vendorPONo=`"${vendorPONo}"`;
                }
                Log.Info("-------------vendorPONo-----------------------" + vendorPONo);

                var vendorPOItem = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Vendor PO Item'));
                if(vendorPOItem){
                    vendorPOItem=`"${vendorPOItem}"`;
                }
                Log.Info("-------------vendorPOItem-----------------------" + vendorPOItem);

                var POETDDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO ETD Date'));
                if(POETDDate){
                    POETDDate=`"${POETDDate}"`;
                }
                Log.Info("-------------POETDDate-----------------------" + POETDDate);

                var firstDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_PO ETD First Date'));
                if(firstDate){
                    firstDate=`"${firstDate}"`;
                }
                Log.Info("-------------firstDate-----------------------" + firstDate);

                var statusRTP = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_RTP(Y/N)'));
                if(statusRTP){
                    statusRTP=`"${statusRTP}"`;
                }
                Log.Info("-------------statusRTP-----------------------" + statusRTP);

                var planDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Production Plan Date'));
                if(planDate){
                    planDate = `"${planDate}"`;
                }
                Log.Info("-------------planDate-----------------------" + planDate);

                var closingDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Production Closing Date'));
                if(closingDate){
                    closingDate=`"${closingDate}"`;
                }
                Log.Info("-------------closingDate-----------------------" + closingDate);

                var outDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Gate Out Date'));
                if(outDate){
                    outDate=`"${outDate}"`;
                }
                Log.Info("-------------outDate-----------------------" + outDate);

                var plannedETDDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Planned ETD Date'));
                if(plannedETDDate){
                    plannedETDDate=`"${plannedETDDate}"`;
                }
                Log.Info("-------------plannedETDDate-----------------------" + plannedETDDate);

                var changeETADate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Change ETA Date'));
                if(changeETADate){
                    changeETADate=`"${changeETADate}"`;
                }
                Log.Info("-------------changeETADate-----------------------" + changeETADate);

                var history = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_History'));
                if(history){
                    history=`"${history}"`;
                }
                Log.Info("-------------history-----------------------" + history);

                var updateTime = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Update time'));
                if(updateTime){
                    updateTime=`"${updateTime}"`;
                }
                Log.Info("-------------updateTime-----------------------" + updateTime);

                var updatedby = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Updated by'));
                if(updatedby){
                    updatedby=`"${updatedby}"`;
                }
                Log.Info("-------------updatedby-----------------------" + updatedby);

                var ATADate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ATA Date'));
                if(ATADate){
                    ATADate=`"${ATADate}"`;
                }
                Log.Info("-------------ATADate-----------------------" + ATADate);

                var SONo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_SO No'));
                if(SONo){
                    SONo=`"${SONo}"`;
                }
                Log.Info("-------------SONo-----------------------" + SONo);

                var SOItem = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_SO Item'));
                if(SOItem){
                    SOItem=`"${SOItem}"`;
                }
                Log.Info("-------------SOItem-----------------------" + SOItem);

                var SODate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_SO Date'));
                if(SODate){
                    SODate=`"${SODate}"`;
                }
                Log.Info("-------------SODate-----------------------" + SODate);

                var localAmt = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Local Amt'));
                if(localAmt){
                    localAmt=`"${localAmt}"`;
                }
                Log.Info("-------------localAmt-----------------------" + localAmt);

                var USDAmt = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_USD Amt'));
                if(USDAmt){
                    USDAmt=`"${USDAmt}"`;
                }
                Log.Info("-------------USDAmt-----------------------" + USDAmt);

                var containerNo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Container No'));
                if(containerNo){
                    containerNo=`"${containerNo}"`;
                }
                Log.Info("-------------containerNo-----------------------" + containerNo);

                var containerType = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Container Type'));
                if(containerType){
                    containerType=`"${containerType}"`;
                }
                Log.Info("-------------containerType-----------------------" + containerType);

                var requestDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_CNTR Arrange Request Date'));
                if(requestDate){
                    requestDate=`"${requestDate}"`;
                }
                Log.Info("-------------requestDate-----------------------" + requestDate);

                var INDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Empty CNTR Gate IN Date'));
                if(INDate){
                    INDate=`"${INDate}"`;
                }
                Log.Info("-------------INDate-----------------------" + INDate);

                var facDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_CNTR Gate Out Ex-fac Date'));
                if(facDate){
                    facDate=`"${facDate}"`;
                }
                Log.Info("-------------facDate-----------------------" + facDate);

                var BRNo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_BR No'));
                if(BRNo){
                    BRNo=`"${BRNo}"`;
                }
                Log.Info("-------------BRNo-----------------------" + BRNo);

                var BRDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_BR Date'));
                if(BRDate){
                    BRDate=`"${BRDate}"`;
                }
                Log.Info("-------------BRDate-----------------------" + BRDate);

                var BCNo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_BC No'));
                if(BCNo){
                    BCNo=`"${BCNo}"`;
                }
                Log.Info("-------------BCNo-----------------------" + BCNo);

                var BCDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_BC Date'));
                if(BCDate){
                    BCDate=`"${BCDate}"`;
                }
                Log.Info("-------------BCDate-----------------------" + BCDate);

                var portCode = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Depart Port Code'));
                if(portCode){
                    portCode=`"${portCode}"`;
                }
                Log.Info("-------------partCode-----------------------" + portCode);

                var portName = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Depart Port Name'));
                if(portName){
                    portName=`"${portName}"`;
                }
                Log.Info("-------------portName-----------------------" + portName);

                var arrivePortCode = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Arrive Port Code'));
                if(arrivePortCode){
                    arrivePortCode=`"${arrivePortCode}"`;
                }
                Log.Info("-------------arrivePortCode-----------------------" + arrivePortCode);

                var arrivePortName = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Arrive Port Name'));
                if(arrivePortName){
                    arrivePortName=`"${arrivePortName}"`;
                }
                Log.Info("-------------arrivePortName-----------------------" + arrivePortName);

                var destination = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Destination'));
                if(destination){
                    destination=`"${destination}"`;
                }
                Log.Info("-------------destination-----------------------" + destination);

                var incoterms = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Incoterms'));
                if(incoterms){
                    incoterms=`"${incoterms}"`;
                }
                Log.Info("-------------incoterms-----------------------" + incoterms);

                var incoterms2 = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Incoterms2'));
                if(incoterms2){
                    incoterms2=`"${incoterms2}"`;
                }
                Log.Info("-------------incoterms2-----------------------" + incoterms2);

                var closeTime = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Close Time'));
                if(closeTime){
                    closeTime=`"${closeTime}"`;
                }
                Log.Info("-------------closeTime-----------------------" + closeTime);

                var SRNo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_SR No'));
                if(SRNo){
                    SRNo=`"${SRNo}"`;
                }
                Log.Info("-------------SRNo-----------------------" + SRNo);

                var SRStatus = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_SR Status'));
                if(SRStatus){
                    SRStatus=`"${SRStatus}"`;
                }
                Log.Info("-------------SRStatus-----------------------" + SRStatus);

                var SRIssueDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_SR Issue Date'));
                if(SRIssueDate){
                    SRIssueDate=`"${SRIssueDate}"`;
                }
                Log.Info("-------------SRIssueDate-----------------------" + SRIssueDate);

                var companyCode = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Ship Company Code'));
                if(companyCode){
                    companyCode=`"${companyCode}"`;
                }
                Log.Info("-------------companyCode-----------------------" + companyCode);

                var companyName = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Ship Company Name'));
                if(companyName){
                    companyName=`"${companyName}"`;
                }
                Log.Info("-------------companyName-----------------------" + companyName);

                var vesselName = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Vessel Name'));
                if(vesselName){
                    vesselName=`"${vesselName}"`;
                }
                Log.Info("-------------vesselName-----------------------" + vesselName);

                var BLNo = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_BL No'));
                if(BLNo){
                    BLNo=`"${BLNo}"`;
                }
                Log.Info("-------------BLNo-----------------------" + BLNo);

                var BLStatus = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_BL Status'));
                if(BLStatus){
                    BLStatus=`"${BLStatus}"`;
                }
                Log.Info("-------------BLStatus-----------------------" + BLStatus);

                var ATAWeekDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ATA Week Date'));
                if(ATAWeekDate){
                    ATAWeekDate=`"${ATAWeekDate}"`;
                }
                Log.Info("-------------ATAWeekDate-----------------------" + ATAWeekDate);

                var ATDWeekDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ATD Week Date'));
                if(ATDWeekDate){
                    ATDWeekDate=`"${ATDWeekDate}"`;
                }
                Log.Info("-------------ATDWeekDate-----------------------" + ATDWeekDate);

                var chkFlag = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Chk Flag'));
                if(chkFlag){
                    chkFlag=`"${chkFlag}"`;
                }
                Log.Info("-------------chkFlag-----------------------" + chkFlag);

                var DOItem = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_DO Item'));
                if(DOItem){
                    DOItem=`"${DOItem}"`;
                }
                Log.Info("-------------DOItem-----------------------" + DOItem);

                var ETAWeekDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ETA Week Date'));
                if(ETAWeekDate){
                    ETAWeekDate=`"${ETAWeekDate}"`;
                }
                Log.Info("-------------ETAWeekDate-----------------------" + ETAWeekDate);

                var ETDWeekDate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_ETD Week Date'));
                if(ETDWeekDate){
                    ETDWeekDate=`"${ETDWeekDate}"`;
                }
                Log.Info("-------------ETDWeekDate-----------------------" + ETDWeekDate);

                var forwarder = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Forwarder'));
                if(forwarder){
                    forwarder=`"${forwarder}"`;
                }
                Log.Info("-------------forwarder-----------------------" + forwarder);

                var plannedETADate = query.row(0).cell(query.measureColumnIndex('Out PO Tracking Status_Planned ETA Date'));
                if(plannedETADate){
                    plannedETADate=`"${plannedETADate}"`;
                }
                Log.Info("-------------plannedETADate-----------------------" + plannedETADate);

                var seq2 = curr.fbSeq2.Value;

                //var queryPartialPO = `Select ([Version].[Version Name].[CurrentWorkingView] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sales Domain].[Sales Lv3 Name] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type] * [Project].[Project] * [ERP Ship to].[ERP Ship to ID] * [Seq].[Seq] * [Seq2].[Seq2].[${curr.fbSeq2.Value}] ) on row, ({Measure.[Out PO Tracking Status_Reason Category], Measure.[Out PO Tracking Status_Partial Qty], Measure.[Out PO Tracking Status_PO Qty], Measure.[Out PO Tracking Status_DO No], Measure.[Out PO Tracking Status_PO Seq]}) on column;`;
                var queryPartialPO = `Select ([Version].[Version Name].[${props.fbVersion}] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type] * [ERP Ship to].[ERP Ship to ID] * [Seq].[Seq] * [Seq2].[Seq2].[${curr.fbSeq2.Value}] ) on row, ({Measure.[Out PO Tracking Status_Reason Category], Measure.[Out PO Tracking Status_Partial Qty], Measure.[Out PO Tracking Status_PO Qty], Measure.[Out PO Tracking Status_DO No], Measure.[Out PO Tracking Status_PO Seq]}) on column;`;
    
                queryPartialPO = cellsetModule.createCellSet(queryModule.select(queryPartialPO));
    
                Log.Info("-------------queryPartialPO-----------------------" + queryPartialPO);
    
                for(let j=0; j<queryPartialPO.rowCount; j++){
                    var tempPOSeq = queryPartialPO.row(j).cell(queryPartialPO.measureColumnIndex('Out PO Tracking Status_PO Seq'));
                    if(tempPOSeq>POSeq){
                        POSeq=tempPOSeq;
                        seq2 = queryPartialPO.row(j).cell(queryPartialPO.memberColumnIndex('Seq2','Seq2')).Name;
                    }
                }

                var count = props.fbPartialPOCount;

                for(let j=1; j<=count; j++){
                    var seqValue = j+POSeq;
                    //var updateQuery = `cartesian scope: ([Version].[Version Name].[CurrentWorkingView] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sales Domain].[Sales Lv3 Name].[${curr.fbAP2.Value}] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type].[${curr.fbOutsourcingType.Value}] * [Project].[Project].[${curr.fbProject.Value}] * [ERP Ship to].[ERP Ship to ID].[${curr.fbERPShipTo.Value}] * [Seq].[Seq].[${seqValue}] * [Seq2].[Seq2].[${seq2}]); Measure.[Out PO Tracking Status_PO Seq]=${seqValue}; Measure.[Out PO Tracking Status_Delivery Status]=${delStatus}; Measure.[Out PO Tracking Status_PO No]=${PONo}; Measure.[Out PO Tracking Status_PO Item]=${POItem}; Measure.[Out PO Tracking Status_Document Type]=${docType};
                    var updateQuery = `cartesian scope: ([Version].[Version Name].[${props.fbVersion}] * [Time].[Week].[${curr.fbTime.Value}] * [Item].[Item].[${curr.fbItem.Value}] * [Location].[Location].[${curr.fbLocation.Value}] * [Sub Location].[Sub Location].[${curr.fbSubLocation.Value}] * [Outsourcing Type].[Outsourcing Type].[${curr.fbOutsourcingType.Value}] * [ERP Ship to].[ERP Ship to ID].[${curr.fbERPShipTo.Value}] * [Seq].[Seq].[${seqValue}] * [Seq2].[Seq2].[${seq2}]); Measure.[Out PO Tracking Status_PO Seq]=${seqValue}; Measure.[Out PO Tracking Status_Delivery Status]=${delStatus}; Measure.[Out PO Tracking Status_PO No]=${PONo}; Measure.[Out PO Tracking Status_PO Item]=${POItem}; Measure.[Out PO Tracking Status_Document Type]=${docType};
                    Measure.[Out PO Tracking Status_Purchase ORG]=${purORG};
                    Measure.[Out PO Tracking Status_PO Create Date]=${createDate};
                    Measure.[Out PO Tracking Status_PO Qty]=${POQty};
                    Measure.[Out PO Tracking Status_GR Qty]=${GRQty};
                    Measure.[Out PO Tracking Status_Remain Qty]=${remainQty};
                    Measure.[Out PO Tracking Status_Partial Qty]=null;
                    Measure.[Out PO Tracking Status_GR Date]=${GRDate};
                    Measure.[Out PO Tracking Status_DO Qty]=${DOQty};
                    Measure.[Out PO Tracking Status_DO Create Date]=${DOcreateDate};
                    Measure.[Out PO Tracking Status_ETD Week]=${ETDWeek};
                    Measure.[Out PO Tracking Status_ETA Week]=${ETAWeek};
                    Measure.[Out PO Tracking Status_Planned ETD Week]=${plannedETDWeek};
                    Measure.[Out PO Tracking Status_Planned ETA Week]=${plannedETAWeek};
                    Measure.[Out PO Tracking Status_ATD Week]=${ATDWeek};
                    Measure.[Out PO Tracking Status_ATA Week]=${ATAWeek};
                    Measure.[Out PO Tracking Status_Vendor PO No]=${vendorPONo};
                    Measure.[Out PO Tracking Status_Vendor PO Item]=${vendorPOItem};
                    Measure.[Out PO Tracking Status_PO ETD Date]=${POETDDate};
                    Measure.[Out PO Tracking Status_PO ETD First Date]=${firstDate};
                    Measure.[Out PO Tracking Status_RTP(Y/N)]=${statusRTP};
                    Measure.[Out PO Tracking Status_Production Plan Date]=${planDate};
                    Measure.[Out PO Tracking Status_Production Closing Date]=${closingDate};
                    Measure.[Out PO Tracking Status_Gate Out Date]=${outDate};
                    Measure.[Out PO Tracking Status_Planned ETD Date]=${plannedETDDate};
                    Measure.[Out PO Tracking Status_Change ETA Date]=${changeETADate};
                    Measure.[Out PO Tracking Status_History]=${history};
                    Measure.[Out PO Tracking Status_Update time]=${updateTime};
                    Measure.[Out PO Tracking Status_Updated by]=${updatedby};
                    Measure.[Out PO Tracking Status_ATA Date]=${ATADate};
                    Measure.[Out PO Tracking Status_SO No]=${SONo};
                    Measure.[Out PO Tracking Status_SO Item]=${SOItem};
                    Measure.[Out PO Tracking Status_SO Date]=${SODate};
                    Measure.[Out PO Tracking Status_Local Amt]=${localAmt};
                    Measure.[Out PO Tracking Status_USD Amt]=${USDAmt};
                    Measure.[Out PO Tracking Status_Container No]=${containerNo};
                    Measure.[Out PO Tracking Status_Container Type]=${containerType};
                    Measure.[Out PO Tracking Status_CNTR Arrange Request Date]=${requestDate};
                    Measure.[Out PO Tracking Status_Empty CNTR Gate IN Date]=${INDate};
                    Measure.[Out PO Tracking Status_CNTR Gate Out Ex-fac Date]=${facDate};
                    Measure.[Out PO Tracking Status_BR No]=${BRNo};
                    Measure.[Out PO Tracking Status_BR Date]=${BRDate};
                    Measure.[Out PO Tracking Status_BC No]=${BCNo};
                    Measure.[Out PO Tracking Status_BC Date]=${BCDate};
                    Measure.[Out PO Tracking Status_Depart Port Code]=${portCode};
                    Measure.[Out PO Tracking Status_Depart Port Name]=${portName};
                    Measure.[Out PO Tracking Status_Arrive Port Code]=${arrivePortCode};
                    Measure.[Out PO Tracking Status_Arrive Port Name]=${arrivePortName};
                    Measure.[Out PO Tracking Status_Destination]=${destination};
                    Measure.[Out PO Tracking Status_Incoterms]=${incoterms};
                    Measure.[Out PO Tracking Status_Incoterms2]=${incoterms2};
                    Measure.[Out PO Tracking Status_Close Time]=${closeTime};
                    Measure.[Out PO Tracking Status_SR No]=${SRNo};
                    Measure.[Out PO Tracking Status_SR Status]=${SRStatus};
                    Measure.[Out PO Tracking Status_SR Issue Date]=${SRIssueDate};
                    Measure.[Out PO Tracking Status_Ship Company Code]=${companyCode};
                    Measure.[Out PO Tracking Status_Vessel Name]=${vesselName};
                    Measure.[Out PO Tracking Status_BL No]=${BLNo};
                    Measure.[Out PO Tracking Status_BL Status]=${BLStatus};
                    Measure.[Out PO Tracking Status_ATA Week Date]=${ATAWeekDate};
                    Measure.[Out PO Tracking Status_ATD Week Date]=${ATDWeekDate};
                    Measure.[Out PO Tracking Status_Chk Flag]=${chkFlag};
                    Measure.[Out PO Tracking Status_DO Item]=${DOItem};
                    Measure.[Out PO Tracking Status_DO No]=${DONo};
                    Measure.[Out PO Tracking Status_ETA Week Date]=${ETAWeekDate};
                    Measure.[Out PO Tracking Status_ETD Week Date]=${ETDWeekDate};
                    Measure.[Out PO Tracking Status_Forwarder]=${forwarder};
                    Measure.[Out PO Tracking Status_Planned ETA Date]=${plannedETADate};
                    Measure.[Out PO Tracking Status_Ship Company Name]=${companyName};
                    end scope;`;
                    queryModule.update(updateQuery);
                }
            }
        }
        catch (e) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
            return;
        }
        };

    return {
        validation: validation,
        AddPartialPO: AddPartialPO
    };
});