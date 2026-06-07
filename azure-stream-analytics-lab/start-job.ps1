$RG="GL-EVENT-PROC"

$JOB="telecomfakecallsjob"

az stream-analytics job start `
--resource-group $RG `
--name $JOB `
--output-start-mode JobStartTime