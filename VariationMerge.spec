/*
A KBase module: VariationMerge
*/

module VariationMerge {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */

    typedef structure{
        string workspace_name; 
        list <string> vcflist; 
        string variation_object_name;  
    } inparams;
   
    typedef structure {
        string report_name;
        string report_ref;
    } OutResults; 

    funcdef run_VariationMerge(inparams params) returns (OutResults output) authentication required;

};
