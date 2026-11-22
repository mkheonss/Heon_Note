define('o9.NSCM.JSSCSSolverCount', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    
    const programName = "o9.NSCM.JSSCSSolverCount";

	var fn_count = function(o9Params){
        try {
	        const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            const queries = [
                // - df_in_01 : Select ([Item].[Item]);
                ["Dimension", "ITEM", "[Item].[Item]"],
                // - df_in_02 : Select ([Location].[Location]);
                ["Dimension", "LOCATION", "[Location].[Location]"],
                // - df_in_03 : Select ([Activity1].[Activity1]);
                ["Dimension", "ACTIVITY1", "[Activity1].[Activity1]"],
                // - df_in_04 : Select ([Activity2].[Activity2]);
                ["Dimension", "ACTIVITY2", "[Activity2].[Activity2]"],
                // - df_in_05 : Select ([Activity3].[Activity3]);
                ["Dimension", "ACTIVITY3", "[Activity3].[Activity3]"],
                // - df_in_06 : Select ([Resource Group].[Resource Group]);
                ["Dimension", "RESOURCE GROUP", "[Resource Group].[Resource Group]"],
                // - df_in_07 : Select ([Resource].[Resource]);
                ["Dimension", "RESOURCE", "[Resource].[Resource]"],
                // - df_in_08 : Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[Dummy]}) on column;
                ["Measure Group", "BOM Master", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [BOM Info].[BOM ID] * {Measure.[BOM Master_BOM ID], Measure.[Dummy]}"],
                // - df_in_09 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Comp_BOM ID Location], Measure.[Dummy]}) on column;
                ["Measure Group", "BOM Component", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [BOM Info].[BOM ID] * {Measure.[BOM Comp_BOM ID Location], Measure.[Dummy]}"],
                // - df_in_10 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Asn], Measure.[Dummy]}) on column;
                ["Measure Group", "BOD Item", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * {Measure.[BOD Item_Asn], Measure.[Dummy]}"],
                // - df_in_11 : Select ([Version].[Version Name]) on row, ({Measure.[W Plan Start Bucket]}) on column;
                ["Measure Group", "001.001W Solver Inputs Planning Parameters", "[Version].[Version Name].[CWV_MP] * {Measure.[W Plan Start Bucket]}"],
                // - df_in_12 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Material Consumption Association], Measure.[Dummy]}) on column;
                ["Measure Group", "001.002W Solver Inputs Material Consumption Association", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Material Consumption Association], Measure.[Dummy]}"],
                // - df_in_13 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Priority], Measure.[Dummy]}) on column;
                ["Measure Group", "001.003W Solver Inputs Material Production Association", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Activity Priority], Measure.[Dummy]}"],
                // - df_in_14 : Select ([Version].[Version Name] * [Location].[Location] * [Resource].[Resource] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Input Resource Priority], Measure.[Dummy]}) on column;
                ["Measure Group", "001.004W Solver Inputs Capacity Consumption Association", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Resource].[Resource] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Input Resource Priority], Measure.[Dummy]}"],
                // - df_in_15 : Select ([Version].[Version Name] * [Location].[Location] * [Resource Group].[Resource Group] * [Resource].[Resource] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Simultaneous Capacity Consumption Association], Measure.[Dummy]}) on column;
                ["Measure Group", "001.005W Solver Inputs Resource Group Consumption Association", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Resource Group].[Resource Group] * [Resource].[Resource] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Simultaneous Capacity Consumption Association], Measure.[Dummy]}"],
                // - df_in_16 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Material Consumed Quantity Per Time Varying], Measure.[Dummy]}) on column;
                ["Measure Group", "001.006W Solver Inputs Quantity Per Time Varying", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Material Consumed Quantity Per Time Varying], Measure.[Dummy]}"],
                // - df_in_17 : Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Cost Per Unit], Measure.[Dummy]}) on column;
                ["Measure Group", "001.007W Solver Inputs Activity Parameters", "[Version].[Version Name].[CWV_MP] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Activity Cost Per Unit], Measure.[Dummy]}"],
                // - df_in_18 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Priority Time Varying], Measure.[Dummy]}) on column;
                ["Measure Group", "001.008W Solver Inputs Activity Share", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Activity Priority Time Varying], Measure.[Dummy]}"],
                // - df_in_19 : Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Frozen Window], Measure.[Dummy]}) on column;
                ["Measure Group", "001.009W Solver Inputs Frozen Window", "[Version].[Version Name].[CWV_MP] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Frozen Window], Measure.[Dummy]}"],
                // - df_in_20 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W LotSize Increment], Measure.[Dummy]}) on column;
                ["Measure Group", "001.010W Solver Inputs LotSize Parameters", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W LotSize Increment], Measure.[Dummy]}"],
                // - df_in_21 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[W Alternate Material Node Group Priority], Measure.[Dummy]}) on column;
                ["Measure Group", "001.011W Solver Inputs Inventory Node Parameters", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * {Measure.[W Alternate Material Node Group Priority], Measure.[Dummy]}"],
                // - df_in_22 : Select ([Version].[Version Name] * [Resource Group].[Resource Group] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Input Resource Group Priority], Measure.[Dummy]}) on column;
                ["Measure Group", "001.015W Solver Inputs Resource Group Priority", "[Version].[Version Name].[CWV_MP] * [Resource Group].[Resource Group] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Input Resource Group Priority], Measure.[Dummy]}"],
                // - df_in_23 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[W Cascading RCA Limit], Measure.[Dummy]}) on column;
                ["Measure Group", "001.018W Solver Inputs Demand Time Granularity", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] * {Measure.[W Cascading RCA Limit], Measure.[Dummy]}"],
                // - df_in_24 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] ) on row, ({Measure.[W Material Node for Demand Split], Measure.[Dummy]}) on column;
                ["Measure Group", "001.019W Solver Inputs Inventory Inputs", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * {Measure.[W Material Node for Demand Split], Measure.[Dummy]}"],
                // - df_in_25 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Documents].[OrderlineID] ) on row, ({Measure.[W Expected Receipts], Measure.[Dummy]}) on column;
                ["Measure Group", "001.020W Solver Inputs Inventory Inputs By OrderLine ID", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Documents].[OrderlineID] * {Measure.[W Expected Receipts], Measure.[Dummy]}"],
                // - df_in_26 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Consume Outbound Capacity], Measure.[Dummy]}) on column;
                ["Measure Group", "001.021W Solver Inputs WIP", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Consume Outbound Capacity], Measure.[Dummy]}"],
                // - df_in_27 : Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Resource].[Resource] ) on row, ({Measure.[W Capacity Incremental Flag], Measure.[Dummy]}) on column;
                ["Measure Group", "001.022W Solver Inputs Capacity", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Resource].[Resource] * {Measure.[W Capacity Incremental Flag], Measure.[Dummy]}"],
                // - df_in_28 : Select ([Version].[Version Name] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [Location].[Location] * [Time].[Week] * [Resource].[Resource] ) on row, ({Measure.[W LP Flex Capacity], Measure.[Dummy]}) on column;
                ["Measure Group", "001.48W LP Solver Flex Capacity Input", "[Version].[Version Name].[CWV_MP] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [Location].[Location] * [Time].[Week] * [Resource].[Resource] * {Measure.[W LP Flex Capacity], Measure.[Dummy]}"],
                // - df_in_29 : Select ([Version].[Version Name] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Lead Time Time Varying], Measure.[Dummy]}) on column;
                ["Measure Group", "001.49W Activity Lead Time Time Varying", "[Version].[Version Name].[CWV_MP] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Activity Lead Time Time Varying], Measure.[Dummy]}"],
                // - df_in_30 : Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Resource].[Resource] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Resource Consumed Time Varying Quantity Per], Measure.[Dummy]}) on column;
                ["Measure Group", "280.001W MFG Resource Consumed Time Varying Quantity Per", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Resource].[Resource] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * {Measure.[W Resource Consumed Time Varying Quantity Per], Measure.[Dummy]}"],
                // - df_in_31 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[W Alternate Item Input Final Association], Measure.[Dummy]}) on column;
                ["Measure Group", "014.002W Network Intermediate Item Location Details", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * {Measure.[W Alternate Item Input Final Association], Measure.[Dummy]}"],
                // - df_in_32 : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Multi Level SS Association], Measure.[Dummy]}) on column;
                ["Measure Group", "284.Match Code and Multi Level Location Info", "[Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * {Measure.[Multi Level SS Association], Measure.[Dummy]}"],
                // - df_in_33 : Select ([Version].[Version Name] * [Documents].[OrderlineID] ) on row, ({Measure.[W Original Owner Association], Measure.[Dummy]}) on column;
                ["Measure Group", "283.Original Match Code To OrderID Mapping", "[Version].[Version Name].[CWV_MP] * [Documents].[OrderlineID] * {Measure.[W Original Owner Association], Measure.[Dummy]}"],
                //- df_in_34 : Select ([Version].[Version Name] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [LPObjective].[Objective Type] ) on row, ({Measure.[W LP Active], Measure.[Dummy]}) on column;
                ["Measure Group", "001.040W Solver Inputs LP Objective", "[Version].[Version Name].[CWV_MP] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [LPObjective].[Objective Type] * {Measure.[W LP Active], Measure.[Dummy]}"],
            ];

            const now = new Date();
            const utc = now.getTime() + (now.getTimezoneOffset() * 60 * 1000);
            const krTimeDiff = 9 * 60 * 60 * 1000;
            const nowKr = new Date(utc + krTimeDiff);
            const day = `${nowKr.getFullYear()}-${String(nowKr.getMonth() + 1).padStart(2, '0')}-${String(nowKr.getDate()).padStart(2, '0')}`;
            const time = `${String(nowKr.getHours()).padStart(2, '0')}${String(nowKr.getMinutes()).padStart(2, '0')}${String(nowKr.getSeconds()).padStart(2, '0')}`;
            const versionDisplayName = vdCommon.selectResult('Version.[Version Name].[CWV_MP].DisplayName');

            queries.forEach((query, idx) => {
                const cnt = vdCommon.selectCount(query[2]);
                const dim = ["&CWVUI"
                    ,`[Time].[Day].[${day}]`
                    ,`[Sequence].[Sequence].[${(Number(time) + idx + 1)}]`
                ];
                vdCommon.createMeasure(dim
                    ,[`Measure.[Solver Input Cnt_Data Count]=${cnt};`
                    ,`Measure.[Solver Input Cnt_Dim Mg Type]="${query[0]}";`
                    ,`Measure.[Solver Input Cnt_Target Cube List]="${query[1]}";`
                    ,`Measure.[Solver Input Cnt_Vesion Display Name]="${versionDisplayName}";`
                ]);
            });
            
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
        fn_count : fn_count
    };
});