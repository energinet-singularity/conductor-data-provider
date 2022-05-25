# Generic modules
import logging

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def create_aclinesegment_dataframe(
    dd20_data: pd.DataFrame,
    dd20_to_scada_name_map: pd.DataFrame,
    scada_aclinesegment_map: pd.DataFrame,
    dlr_enabled_col_nm: str = "DLR_ENABLED",
    scada_line_name_col_nm: str = "LINE_EMSNAME",
    translated_name_col_nm: str = "acline_name_translated",
    dd20_name_col_nm="DD20 Name",
    scada_name_col_nm="ETS Name",
) -> pd.DataFrame:
    """
    Combine data from DD20, name mapping and SCADA aclinesegment mapping dataframes, into one single dataframe.
    The resulting dataframe will link data from SCADA system to data from DD20 via the AC-line name.

    The dataframe will contain a record for each AC-Linesegment existing in SCADA, if it can be linked to properties from DD20.
    The AC-Linesegment will only appear in the dataframe if the AC-line name exist in both DD20 and SCADA.
    Each ACLinesegment will be represented by a unique MRID from the SCADA system.

    Parameters
    ----------
    dd20_data : pd.Dataframe
        Dataframe containg data from DD20, where each row represents an AC-line.
    dd20_to_scada_name_map : pd.Dataframe
        Dataframe with mapping from AC-line name in DD20 to AC-line name in SCADA.
        Manualt mapping is used when a translation from DD20 to SCADA AC-line name can not be done automatically.
    scada_aclinesegment_map : pd.Dataframe
        Dataframe with:
        - Mapping from ACLinesegment MRID to ACLine name
        - Flag indicating if Dynamic Line Rating is enabled on the ACLinesegment in SCADA system.
    dlr_enabled_col_nm : str
        (optional) Name of column which contains DLR Enabled flag in SCADA aclinesegment mapping dataframe
        Default = "DLR_ENABLED"
    scada_line_name_col_nm : str
        (optional) Naming of column for holding scada AC-line name.
        The column will be created in combined dataframe and contain either translated name from DD20, or mapped name.
        Default = "LINE_EMSNAME"
    translated_name_col_nm: str
        (optional) Name of column which contains translated in DD20 dataframe.
        Default = "acline_name_translated"
    dd20_name_col_nm: str
        (optional) Name of column which contains DD20 name in name mapping dataframe.
        Default = "DD20 Name"
    scada_name_col_nm: str
        (optional) Name of column which contains SCADA name in name mapping dataframe.
        Default = "ETS Name"
    Returns
    -------
    pd.Dataframe
        Dataframe containing a record for each AC-Linesegment existing in SCADA, if it can be linked to properties from DD20.
    """
    try:
        # Dictionary which maps from dd20 to SCADA name, if mapping is specified.
        acline_namemap_dict = dd20_to_scada_name_map.set_index(
            dd20_name_col_nm
        ).to_dict()[scada_name_col_nm]

        # List which contains either translated name from DD20 or mapped name if existing in mapping dictionary
        mapped_name_list = [
            acline_namemap_dict[x] if x in acline_namemap_dict else x
            for x in dd20_data[translated_name_col_nm]
        ]

        # Creating new column in DD20 data with mapped names and dropping column with translated names
        dd20_data[scada_line_name_col_nm] = mapped_name_list
        dd20_data = dd20_data.drop(columns=[translated_name_col_nm])

        # extract lists of unique line names from conductor and scada dataframe
        lines_in_dd20_data = set(dd20_data[scada_line_name_col_nm].to_list())
        lines_in_scada_data = set(
            scada_aclinesegment_map[scada_line_name_col_nm].to_list()
        )

        # Create list of lines which have DLR enabled flag set True
        lines_dlr_enabled = scada_aclinesegment_map.loc[
            scada_aclinesegment_map[dlr_enabled_col_nm], scada_line_name_col_nm
        ].to_list()

        # Log line names which are in DD20, but not SCADA as warning
        lines_only_in_dd20_data = sorted(
            [
                acline_name
                for acline_name in lines_in_dd20_data
                if acline_name not in lines_in_scada_data
            ]
        )
        if lines_only_in_dd20_data:
            log.warning(
                f"Line(s) with name(s): '{lines_only_in_dd20_data}' exists in conductor data but not in SCADA data."
            )

        # Log line names which are in SCADA, but not DD20 as info
        lines_only_in_scada_data = sorted(
            [
                acline_name
                for acline_name in lines_in_scada_data
                if acline_name not in lines_in_dd20_data
            ]
        )
        if lines_only_in_scada_data:
            log.info(
                f"Line(s) with name(s): '{lines_only_in_scada_data}' exists in SCADA data but not in conductor data."
            )

        # Log lines for which DLR enabled flag is set but data is not availiable in DD20, as errors
        lines_dlr_enabled_data_missing = sorted(
            [
                acline_name
                for acline_name in lines_dlr_enabled
                if acline_name not in lines_in_dd20_data
            ]
        )
        if lines_dlr_enabled_data_missing:
            log.error(
                f"Line(s) with name(s): '{lines_dlr_enabled_data_missing}', are enabled for DLR but has no conductor data."
            )

        # Join two dataframes where AC-line name is the common key.
        dlr_dataframe = scada_aclinesegment_map.join(
            dd20_data.set_index(scada_line_name_col_nm),
            on=scada_line_name_col_nm,
            how="inner",
        )

        # force uppercase on all columns
        dlr_dataframe.columns = dlr_dataframe.columns.str.upper()

        return dlr_dataframe

    except Exception as e:
        log.exception(f"Combining data to ACLinesegment dataframe failed with message: {e}.")
        raise e