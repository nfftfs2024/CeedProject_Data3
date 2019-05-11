@ECHO OFF
CLS
ECHO You are about to execute the TestPackage SSIS package
PAUSE
"C:\Program Files\Microsoft SQL Server\140\DTS\Binn\DTEXEC.exe" /File "C:\Users\JamesC\OneDrive - Queensland University of Technology\IFN701Project\Deliverable\VSCode\SSIS\FAQGeneration_wk\FAQGeneration_wk\Package.dtsx"
PAUSE