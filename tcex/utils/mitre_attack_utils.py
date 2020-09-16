"""TcEx Mitre Attack Utilities Module"""
# standard library
from typing import List

# flake8: noqa
MITRE_ATTACK_TAGS = """T1001 - Data Obfuscation - C&C - ENT - ATT&CK
T1003 - OS Credential Dumping - CRA - ENT - ATT&CK
T1005 - Data from Local System - COL - ENT - ATT&CK
T1006 - Direct Volume Access - DEF - ENT - ATT&CK
T1007 - System Service Discovery - DIS - ENT - ATT&CK
T1008 - Fallback Channels - C&C - ENT - ATT&CK
T1010 - Application Window Discovery - DIS - ENT - ATT&CK
T1011 - Exfiltration Over Other Network Medium - EXF - ENT - ATT&CK
T1012 - Query Registry - DIS - ENT - ATT&CK
T1014 - Rootkit - DEF - ENT - ATT&CK
T1016 - System Network Configuration Discovery - DIS - ENT - ATT&CK
T1018 - Remote System Discovery - DIS - ENT - ATT&CK
T1020 - Automated Exfiltration - EXF - ENT - ATT&CK
T1021 - Remote Services - LAT - ENT - ATT&CK
T1021.001 - Remote Desktop Protocol - LAT - ENT - ATT&CK
T1021.002 - SMB/Windows Admin Shares - LAT - ENT - ATT&CK
T1021.006 - Windows Remote Management - EXE - ENT - ATT&CK
T1021.006 - Windows Remote Management - LAT - ENT - ATT&CK
T1021.006 - Windows Remote Management - NDT - ENT - ATT&CK
T1025 - Data from Removable Media - COL - ENT - ATT&CK
T1027 - Obfuscated Files or Information - DEF - ENT - ATT&CK
T1027.001 - Binary Padding - DEF - ENT - ATT&CK
T1027.002 - Software Packing - DEF - ENT - ATT&CK
T1027.004 - Compile After Delivery - DEF - ENT - ATT&CK
T1027.005 - Indicator Removal from Tools - DEF - ENT - ATT&CK
T1029 - Scheduled Transfer - EXF - ENT - ATT&CK
T1030 - Data Transfer Size Limits - EXF - ENT - ATT&CK
T1033 - System Owner/User Discovery - DIS - ENT - ATT&CK
T1036 - Masquerading - DEF - ENT - ATT&CK
T1036.006 - Space after Filename - DEF - ENT - ATT&CK
T1036.006 - Space after Filename - EXE - ENT - ATT&CK
T1036.006 - Space after Filename - NDT - ENT - ATT&CK
T1037 - Boot or Logon Initialization Scripts - LAT - ENT - ATT&CK
T1037 - Boot or Logon Initialization Scripts - PER - ENT - ATT&CK
T1037 - Boot or Logon Initialization Scripts - NDT - ENT - ATT&CK
T1037.004 - Rc.common - PER - ENT - ATT&CK
T1037.005 - Startup Items - PER - ENT - ATT&CK
T1037.005 - Startup Items - PRI - ENT - ATT&CK
T1037.005 - Startup Items - NDT - ENT - ATT&CK
T1039 - Data from Network Shared Drive - COL - ENT - ATT&CK
T1040 - Network Sniffing - CRA - ENT - ATT&CK
T1040 - Network Sniffing - DIS - ENT - ATT&CK
T1040 - Network Sniffing - NDT - ENT - ATT&CK
T1041 - Exfiltration Over C2 Channel - EXF - ENT - ATT&CK
T1046 - Network Service Scanning - DIS - ENT - ATT&CK
T1047 - Windows Management Instrumentation - EXE - ENT - ATT&CK
T1048 - Exfiltration Over Alternative Protocol - EXF - ENT - ATT&CK
T1049 - System Network Connections Discovery - DIS - ENT - ATT&CK
T1052 - Exfiltration Over Physical Medium - EXF - ENT - ATT&CK
T1053 - Scheduled Task/Job - EXE - ENT - ATT&CK
T1053 - Scheduled Task/Job - EXE - ENT - ATT&CK
T1053 - Scheduled Task/Job - PER - ENT - ATT&CK
T1053 - Scheduled Task/Job - PER - ENT - ATT&CK
T1053 - Scheduled Task/Job - PRI - ENT - ATT&CK
T1053 - Scheduled Task/Job - NDT - ENT - ATT&CK
T1055 - Process Injection - DEF - ENT - ATT&CK
T1055 - Process Injection - PRI - ENT - ATT&CK
T1055 - Process Injection - NDT - ENT - ATT&CK
T1055.011 - Extra Window Memory Injection - DEF - ENT - ATT&CK
T1055.011 - Extra Window Memory Injection - PRI - ENT - ATT&CK
T1055.011 - Extra Window Memory Injection - NDT - ENT - ATT&CK
T1055.012 - Process Hollowing - DEF - ENT - ATT&CK
T1055.013 - Process Doppelgänging - DEF - ENT - ATT&CK
T1056 - Input Capture - COL - ENT - ATT&CK
T1056 - Input Capture - CRA - ENT - ATT&CK
T1056 - Input Capture - NDT - ENT - ATT&CK
T1056.002 - GUI Input Capture - CRA - ENT - ATT&CK
T1056.004 - Credential API Hooking - CRA - ENT - ATT&CK
T1056.004 - Credential API Hooking - PER - ENT - ATT&CK
T1056.004 - Credential API Hooking - PRI - ENT - ATT&CK
T1056.004 - Credential API Hooking - NDT - ENT - ATT&CK
T1057 - Process Discovery - DIS - ENT - ATT&CK
T1059 - Command and Scripting Interpreter - EXE - ENT - ATT&CK
T1059.001 - PowerShell - EXE - ENT - ATT&CK
T1059.002 - AppleScript - EXE - ENT - ATT&CK
T1059.002 - AppleScript - LAT - ENT - ATT&CK
T1059.002 - AppleScript - NDT - ENT - ATT&CK
T1068 - Exploitation for Privilege Escalation - PRI - ENT - ATT&CK
T1069 - Permission Groups Discovery - DIS - ENT - ATT&CK
T1070 - Indicator Removal on Host - DEF - ENT - ATT&CK
T1070.003 - Clear Command History - DEF - ENT - ATT&CK
T1070.004 - File Deletion - DEF - ENT - ATT&CK
T1070.005 - Network Share Connection Removal - DEF - ENT - ATT&CK
T1070.006 - Timestomp - DEF - ENT - ATT&CK
T1071 - Application Layer Protocol - C&C - ENT - ATT&CK
T1072 - Software Deployment Tools - EXE - ENT - ATT&CK
T1072 - Software Deployment Tools - LAT - ENT - ATT&CK
T1072 - Software Deployment Tools - LAT - ENT - ATT&CK
T1072 - Software Deployment Tools - NDT - ENT - ATT&CK
T1074 - Data Staged - COL - ENT - ATT&CK
T1078 - Valid Accounts - DEF - ENT - ATT&CK
T1078 - Valid Accounts - INI - ENT - ATT&CK
T1078 - Valid Accounts - PER - ENT - ATT&CK
T1078 - Valid Accounts - PRI - ENT - ATT&CK
T1078 - Valid Accounts - NDT - ENT - ATT&CK
T1080 - Taint Shared Content - LAT - ENT - ATT&CK
T1082 - System Information Discovery - DIS - ENT - ATT&CK
T1083 - File and Directory Discovery - DIS - ENT - ATT&CK
T1087 - Account Discovery - DIS - ENT - ATT&CK
T1090 - Proxy - C&C - ENT - ATT&CK
T1090 - Proxy - DEF - ENT - ATT&CK
T1090 - Proxy - NDT - ENT - ATT&CK
T1090.003 - Multi-hop Proxy - C&C - ENT - ATT&CK
T1090.004 - Domain Fronting - C&C - ENT - ATT&CK
T1091 - Replication Through Removable Media - INI - ENT - ATT&CK
T1091 - Replication Through Removable Media - LAT - ENT - ATT&CK
T1091 - Replication Through Removable Media - NDT - ENT - ATT&CK
T1092 - Communication Through Removable Media - C&C - ENT - ATT&CK
T1095 - Non-Application Layer Protocol - C&C - ENT - ATT&CK
T1095 - Non-Application Layer Protocol - C&C - ENT - ATT&CK
T1095 - Non-Application Layer Protocol - NDT - ENT - ATT&CK
T1098 - Account Manipulation - CRA - ENT - ATT&CK
T1098 - Account Manipulation - PER - ENT - ATT&CK
T1098 - Account Manipulation - NDT - ENT - ATT&CK
T1102 - Web Service - C&C - ENT - ATT&CK
T1102 - Web Service - DEF - ENT - ATT&CK
T1102 - Web Service - NDT - ENT - ATT&CK
T1104 - Multi-Stage Channels - C&C - ENT - ATT&CK
T1105 - Ingress Tool Transfer - C&C - ENT - ATT&CK
T1105 - Ingress Tool Transfer - LAT - ENT - ATT&CK
T1105 - Ingress Tool Transfer - NDT - ENT - ATT&CK
T1106 - Native API - EXE - ENT - ATT&CK
T1110 - Brute Force - CRA - ENT - ATT&CK
T1111 - Two-Factor Authentication Interception - CRA - ENT - ATT&CK
T1112 - Modify Registry - DEF - ENT - ATT&CK
T1113 - Screen Capture - COL - ENT - ATT&CK
T1114 - Email Collection - COL - ENT - ATT&CK
T1115 - Clipboard Data - COL - ENT - ATT&CK
T1119 - Automated Collection - COL - ENT - ATT&CK
T1120 - Peripheral Device Discovery - DIS - ENT - ATT&CK
T1123 - Audio Capture - COL - ENT - ATT&CK
T1124 - System Time Discovery - DIS - ENT - ATT&CK
T1125 - Video Capture - COL - ENT - ATT&CK
T1127 - Trusted Developer Utilities Proxy Execution - DEF - ENT - ATT&CK
T1127 - Trusted Developer Utilities Proxy Execution - EXE - ENT - ATT&CK
T1127 - Trusted Developer Utilities Proxy Execution - NDT - ENT - ATT&CK
T1129 - Shared Modules - EXE - ENT - ATT&CK
T1132 - Data Encoding - C&C - ENT - ATT&CK
T1133 - External Remote Services - INI - ENT - ATT&CK
T1133 - External Remote Services - PER - ENT - ATT&CK
T1133 - External Remote Services - NDT - ENT - ATT&CK
T1134 - Access Token Manipulation - DEF - ENT - ATT&CK
T1134 - Access Token Manipulation - PRI - ENT - ATT&CK
T1134 - Access Token Manipulation - NDT - ENT - ATT&CK
T1134.004 - Parent PID Spoofing - DEF - ENT - ATT&CK
T1134.004 - Parent PID Spoofing - PRI - ENT - ATT&CK
T1134.004 - Parent PID Spoofing - NDT - ENT - ATT&CK
T1134.005 - SID-History Injection - PRI - ENT - ATT&CK
T1135 - Network Share Discovery - DIS - ENT - ATT&CK
T1136 - Create Account - PER - ENT - ATT&CK
T1137 - Office Application Startup - PER - ENT - ATT&CK
T1140 - Deobfuscate/Decode Files or Information - DEF - ENT - ATT&CK
T1176 - Browser Extensions - PER - ENT - ATT&CK
T1185 - Man in the Browser - COL - ENT - ATT&CK
T1187 - Forced Authentication - CRA - ENT - ATT&CK
T1189 - Drive-by Compromise - INI - ENT - ATT&CK
T1190 - Exploit Public-Facing Application - INI - ENT - ATT&CK
T1195 - Supply Chain Compromise - INI - ENT - ATT&CK
T1197 - BITS Jobs - DEF - ENT - ATT&CK
T1197 - BITS Jobs - PER - ENT - ATT&CK
T1197 - BITS Jobs - NDT - ENT - ATT&CK
T1199 - Trusted Relationship - INI - ENT - ATT&CK
T1200 - Hardware Additions - INI - ENT - ATT&CK
T1201 - Password Policy Discovery - DIS - ENT - ATT&CK
T1202 - Indirect Command Execution - DEF - ENT - ATT&CK
T1203 - Exploitation for Client Execution - EXE - ENT - ATT&CK
T1204 - User Execution - EXE - ENT - ATT&CK
T1205 - Traffic Signaling - C&C - ENT - ATT&CK
T1205 - Traffic Signaling - DEF - ENT - ATT&CK
T1205 - Traffic Signaling - PER - ENT - ATT&CK
T1205 - Traffic Signaling - NDT - ENT - ATT&CK
T1207 - Rogue Domain Controller - DEF - ENT - ATT&CK
T1210 - Exploitation of Remote Services - LAT - ENT - ATT&CK
T1211 - Exploitation for Defense Evasion - DEF - ENT - ATT&CK
T1212 - Exploitation for Credential Access - CRA - ENT - ATT&CK
T1213 - Data from Information Repositories - COL - ENT - ATT&CK
T1216 - Signed Script Proxy Execution - DEF - ENT - ATT&CK
T1216 - Signed Script Proxy Execution - EXE - ENT - ATT&CK
T1216 - Signed Script Proxy Execution - NDT - ENT - ATT&CK
T1217 - Browser Bookmark Discovery - DIS - ENT - ATT&CK
T1218 - Signed Binary Proxy Execution - DEF - ENT - ATT&CK
T1218 - Signed Binary Proxy Execution - EXE - ENT - ATT&CK
T1218 - Signed Binary Proxy Execution - NDT - ENT - ATT&CK
T1218.001 - Compiled HTML File - DEF - ENT - ATT&CK
T1218.001 - Compiled HTML File - EXE - ENT - ATT&CK
T1218.001 - Compiled HTML File - NDT - ENT - ATT&CK
T1218.002 - Control Panel - DEF - ENT - ATT&CK
T1218.002 - Control Panel - EXE - ENT - ATT&CK
T1218.002 - Control Panel - NDT - ENT - ATT&CK
T1218.003 - CMSTP - DEF - ENT - ATT&CK
T1218.003 - CMSTP - EXE - ENT - ATT&CK
T1218.003 - CMSTP - NDT - ENT - ATT&CK
T1218.004 - InstallUtil - DEF - ENT - ATT&CK
T1218.004 - InstallUtil - EXE - ENT - ATT&CK
T1218.004 - InstallUtil - NDT - ENT - ATT&CK
T1218.005 - Mshta - DEF - ENT - ATT&CK
T1218.005 - Mshta - EXE - ENT - ATT&CK
T1218.005 - Mshta - NDT - ENT - ATT&CK
T1218.007 - Signed Binary Proxy Execution: Msiexec - DEF - ENT - ATT&CK
T1218.009 - Regsvcs/Regasm - DEF - ENT - ATT&CK
T1218.009 - Regsvcs/Regasm - EXE - ENT - ATT&CK
T1218.009 - Regsvcs/Regasm - NDT - ENT - ATT&CK
T1218.010 - Regsvr32 - DEF - ENT - ATT&CK
T1218.010 - Regsvr32 - EXE - ENT - ATT&CK
T1218.010 - Regsvr32 - NDT - ENT - ATT&CK
T1218.011 - Rundll32 - DEF - ENT - ATT&CK
T1218.011 - Rundll32 - EXE - ENT - ATT&CK
T1218.011 - Rundll32 - NDT - ENT - ATT&CK
T1219 - Remote Access Software - C&C - ENT - ATT&CK
T1220 - XSL Script Processing - DEF - ENT - ATT&CK
T1220 - XSL Script Processing - EXE - ENT - ATT&CK
T1220 - XSL Script Processing - NDT - ENT - ATT&CK
T1221 - Template Injection - DEF - ENT - ATT&CK
T1222 - File and Directory Permissions Modification - DEF - ENT - ATT&CK
T1480 - Execution Guardrails - DEF - ENT - ATT&CK
T1482 - Domain Trust Discovery - DIS - ENT - ATT&CK
T1484 - Group Policy Modification - DEF - ENT - ATT&CK
T1485 - Data Destruction - IMP - ENT - ATT&CK
T1486 - Data Encrypted for Impact - IMP - ENT - ATT&CK
T1489 - Service Stop - IMP - ENT - ATT&CK
T1490 - Inhibit System Recovery - IMP - ENT - ATT&CK
T1491 - Defacement - IMP - ENT - ATT&CK
T1495 - Firmware Corruption - IMP - ENT - ATT&CK
T1496 - Resource Hijacking - IMP - ENT - ATT&CK
T1497 - Virtualization/Sandbox Evasion - DEF - ENT - ATT&CK
T1497 - Virtualization/Sandbox Evasion - DIS - ENT - ATT&CK
T1497 - Virtualization/Sandbox Evasion - NDT - ENT - ATT&CK
T1498 - Network Denial of Service - IMP - ENT - ATT&CK
T1499 - Endpoint Denial of Service - IMP - ENT - ATT&CK
T1505 - Server Software Component - PER - ENT - ATT&CK
T1505.003 - Web Shell - PER - ENT - ATT&CK
T1505.003 - Web Shell - PRI - ENT - ATT&CK
T1505.003 - Web Shell - NDT - ENT - ATT&CK
T1518 - Software Discovery - DIS - ENT - ATT&CK
T1518.001 - Security Software Discovery - DIS - ENT - ATT&CK
T1525 - Implant Container Image - PER - ENT - ATT&CK
T1526 - Cloud Service Discovery - DIS - ENT - ATT&CK
T1528 - Steal Application Access Token - CRA - ENT - ATT&CK
T1529 - System Shutdown/Reboot - IMP - ENT - ATT&CK
T1530 - Data from Cloud Storage Object - COL - ENT - ATT&CK
T1531 - Account Access Removal - IMP - ENT - ATT&CK
T1534 - Internal Spearphishing - LAT - ENT - ATT&CK
T1535 - Unused/Unsupported Cloud Regions - DEF - ENT - ATT&CK
T1537 - Transfer Data to Cloud Account - EXF - ENT - ATT&CK
T1538 - Cloud Service Dashboard - DIS - ENT - ATT&CK
T1539 - Steal Web Session Cookie - CRA - ENT - ATT&CK
T1542.001 - System Firmware - PER - ENT - ATT&CK
T1542.002 - Component Firmware - DEF - ENT - ATT&CK
T1542.002 - Component Firmware - PER - ENT - ATT&CK
T1542.002 - Component Firmware - NDT - ENT - ATT&CK
T1542.003 - Bootkit - PER - ENT - ATT&CK
T1543.001 - Launch Agent - PER - ENT - ATT&CK
T1543.002 - Systemd Service - PER - ENT - ATT&CK
T1543.003 - Windows Service - PER - ENT - ATT&CK
T1543.003 - Windows Service - PER - ENT - ATT&CK
T1543.003 - Windows Service - PRI - ENT - ATT&CK
T1543.003 - Windows Service - NDT - ENT - ATT&CK
T1543.004 - Launch Daemon - PER - ENT - ATT&CK
T1543.004 - Launch Daemon - PRI - ENT - ATT&CK
T1543.004 - Launch Daemon - NDT - ENT - ATT&CK
T1546.001 - Change Default File Association - PER - ENT - ATT&CK
T1546.002 - Screensaver - PER - ENT - ATT&CK
T1546.003 - Windows Management Instrumentation Event Subscription - PER - ENT - ATT&CK
T1546.004 - .bash_profile and .bashrc - PER - ENT - ATT&CK
T1546.005 - Trap - EXE - ENT - ATT&CK
T1546.005 - Trap - PER - ENT - ATT&CK
T1546.005 - Trap - NDT - ENT - ATT&CK
T1546.006 - LC_LOAD_DYLIB Addition - PER - ENT - ATT&CK
T1546.007 - Netsh Helper DLL - PER - ENT - ATT&CK
T1546.008 - Accessibility Features - PER - ENT - ATT&CK
T1546.008 - Accessibility Features - PRI - ENT - ATT&CK
T1546.008 - Accessibility Features - NDT - ENT - ATT&CK
T1546.009 - AppCert DLLs - PER - ENT - ATT&CK
T1546.009 - AppCert DLLs - PRI - ENT - ATT&CK
T1546.009 - AppCert DLLs - NDT - ENT - ATT&CK
T1546.010 - AppInit DLLs - PER - ENT - ATT&CK
T1546.010 - AppInit DLLs - PRI - ENT - ATT&CK
T1546.010 - AppInit DLLs - NDT - ENT - ATT&CK
T1546.011 - Application Shimming - PER - ENT - ATT&CK
T1546.011 - Application Shimming - PRI - ENT - ATT&CK
T1546.011 - Application Shimming - NDT - ENT - ATT&CK
T1546.012 - Image File Execution Options Injection - DEF - ENT - ATT&CK
T1546.012 - Image File Execution Options Injection - PER - ENT - ATT&CK
T1546.012 - Image File Execution Options Injection - PRI - ENT - ATT&CK
T1546.012 - Image File Execution Options Injection - NDT - ENT - ATT&CK
T1546.013 - PowerShell Profile - PER - ENT - ATT&CK
T1546.013 - PowerShell Profile - PRI - ENT - ATT&CK
T1546.013 - PowerShell Profile - NDT - ENT - ATT&CK
T1546.014 - Emond - PER - ENT - ATT&CK
T1546.014 - Emond - PRI - ENT - ATT&CK
T1546.014 - Emond - NDT - ENT - ATT&CK
T1546.015 - Component Object Model Hijacking - DEF - ENT - ATT&CK
T1546.015 - Component Object Model Hijacking - PER - ENT - ATT&CK
T1546.015 - Component Object Model Hijacking - NDT - ENT - ATT&CK
T1547.001 - Registry Run Keys / Startup Folder - PER - ENT - ATT&CK
T1547.002 - Authentication Package - PER - ENT - ATT&CK
T1547.003 - Time Providers - PER - ENT - ATT&CK
T1547.004 - Winlogon Helper DLL - PER - ENT - ATT&CK
T1547.005 - Security Support Provider - PER - ENT - ATT&CK
T1547.006 - Kernel Modules and Extensions - PER - ENT - ATT&CK
T1547.007 - Re-opened Applications - PER - ENT - ATT&CK
T1547.008 - LSASS Driver - EXE - ENT - ATT&CK
T1547.008 - LSASS Driver - PER - ENT - ATT&CK
T1547.008 - LSASS Driver - NDT - ENT - ATT&CK
T1547.009 - Shortcut Modification - PER - ENT - ATT&CK
T1547.010 - Port Monitors - PER - ENT - ATT&CK
T1547.010 - Port Monitors - PRI - ENT - ATT&CK
T1547.010 - Port Monitors - NDT - ENT - ATT&CK
T1547.011 - Plist Modification - DEF - ENT - ATT&CK
T1547.011 - Plist Modification - PER - ENT - ATT&CK
T1547.011 - Plist Modification - PER - ENT - ATT&CK
T1547.011 - Plist Modification - PRI - ENT - ATT&CK
T1547.011 - Plist Modification - NDT - ENT - ATT&CK
T1548.001 - Setuid and Setgid - PER - ENT - ATT&CK
T1548.001 - Setuid and Setgid - PRI - ENT - ATT&CK
T1548.001 - Setuid and Setgid - NDT - ENT - ATT&CK
T1548.002 - Bypass User Access Control - DEF - ENT - ATT&CK
T1548.002 - Bypass User Access Control - PRI - ENT - ATT&CK
T1548.002 - Bypass User Access Control - NDT - ENT - ATT&CK
T1548.003 - Sudo and Sudo Caching - PRI - ENT - ATT&CK
T1548.003 - Sudo and Sudo Caching - PRI - ENT - ATT&CK
T1548.003 - Sudo and Sudo Caching - NDT - ENT - ATT&CK
T1548.004 - Elevated Execution with Prompt - PRI - ENT - ATT&CK
T1550.001 - Application Access Token - DEF - ENT - ATT&CK
T1550.001 - Application Access Token - LAT - ENT - ATT&CK
T1550.001 - Application Access Token - NDT - ENT - ATT&CK
T1550.002 - Pass the Hash - LAT - ENT - ATT&CK
T1550.003 - Pass the Ticket - LAT - ENT - ATT&CK
T1550.004 - Web Session Cookie - DEF - ENT - ATT&CK
T1550.004 - Web Session Cookie - LAT - ENT - ATT&CK
T1550.004 - Web Session Cookie - NDT - ENT - ATT&CK
T1552.001 - Credentials In Files - CRA - ENT - ATT&CK
T1552.002 - Credentials in Registry - CRA - ENT - ATT&CK
T1552.003 - Bash History - CRA - ENT - ATT&CK
T1552.004 - Private Keys - CRA - ENT - ATT&CK
T1552.005 - Cloud Instance Metadata API - CRA - ENT - ATT&CK
T1553.001 - Gatekeeper Bypass - DEF - ENT - ATT&CK
T1553.002 - Code Signing - DEF - ENT - ATT&CK
T1553.003 - SIP and Trust Provider Hijacking - DEF - ENT - ATT&CK
T1553.003 - SIP and Trust Provider Hijacking - PER - ENT - ATT&CK
T1553.003 - SIP and Trust Provider Hijacking - NDT - ENT - ATT&CK
T1553.004 - Install Root Certificate - DEF - ENT - ATT&CK
T1555.001 - Keychain - CRA - ENT - ATT&CK
T1555.002 - Securityd Memory - CRA - ENT - ATT&CK
T1555.003 - Credentials from Web Browsers - CRA - ENT - ATT&CK
T1556.002 - Password Filter DLL - CRA - ENT - ATT&CK
T1557.001 - LLMNR/NBT-NS Poisoning and SMB Relay - CRA - ENT - ATT&CK
T1558.003 - Kerberoasting - CRA - ENT - ATT&CK
T1559.002 - Dynamic Data Exchange - EXE - ENT - ATT&CK
T1560 - Archive Collected Data - EXF - ENT - ATT&CK
T1560 - Archive Collected Data - EXF - ENT - ATT&CK
T1560 - Archive Collected Data - NDT - ENT - ATT&CK
T1561.001 - Disk Content Wipe - IMP - ENT - ATT&CK
T1561.002 - Disk Structure Wipe - IMP - ENT - ATT&CK
T1562.001 - Disable or Modify Tools - DEF - ENT - ATT&CK
T1562.003 - HISTCONTROL - DEF - ENT - ATT&CK
T1562.006 - Indicator Blocking - DEF - ENT - ATT&CK
T1563.001 - SSH Hijacking - LAT - ENT - ATT&CK
T1564.001 - Hidden Files and Directories - DEF - ENT - ATT&CK
T1564.001 - Hidden Files and Directories - PER - ENT - ATT&CK
T1564.001 - Hidden Files and Directories - NDT - ENT - ATT&CK
T1564.002 - Hidden Users - DEF - ENT - ATT&CK
T1564.003 - Hidden Window - DEF - ENT - ATT&CK
T1564.004 - NTFS File Attributes - DEF - ENT - ATT&CK
T1565.001 - Stored Data Manipulation - IMP - ENT - ATT&CK
T1565.002 - Transmitted Data Manipulation - IMP - ENT - ATT&CK
T1565.003 - Runtime Data Manipulation - IMP - ENT - ATT&CK
T1566.001 - Spearphishing Attachment - INI - ENT - ATT&CK
T1566.002 - Spearphishing Link - INI - ENT - ATT&CK
T1566.003 - Spearphishing via Service - INI - ENT - ATT&CK
T1568.002 - Domain Generation Algorithms - C&C - ENT - ATT&CK
T1569.001 - Launchctl - DEF - ENT - ATT&CK
T1569.001 - Launchctl - EXE - ENT - ATT&CK
T1569.001 - Launchctl - PER - ENT - ATT&CK
T1569.001 - Launchctl - NDT - ENT - ATT&CK
T1569.002 - Service Execution - EXE - ENT - ATT&CK
T1571 - Non-Standard Port - C&C - ENT - ATT&CK
T1573 - Encrypted Channel - C&C - ENT - ATT&CK
T1573 - Encrypted Channel - C&C - ENT - ATT&CK
T1573 - Encrypted Channel - C&C - ENT - ATT&CK
T1573 - Encrypted Channel - NDT - ENT - ATT&CK
T1574.001 - DLL Search Order Hijacking - DEF - ENT - ATT&CK
T1574.001 - DLL Search Order Hijacking - PER - ENT - ATT&CK
T1574.001 - DLL Search Order Hijacking - PRI - ENT - ATT&CK
T1574.001 - DLL Search Order Hijacking - NDT - ENT - ATT&CK
T1574.002 - DLL Side-Loading - DEF - ENT - ATT&CK
T1574.004 - Dylib Hijacking - PER - ENT - ATT&CK
T1574.004 - Dylib Hijacking - PRI - ENT - ATT&CK
T1574.004 - Dylib Hijacking - NDT - ENT - ATT&CK
T1574.010 - Services File Permissions Weakness - PER - ENT - ATT&CK
T1574.010 - Services File Permissions Weakness - PRI - ENT - ATT&CK
T1574.010 - Services File Permissions Weakness - NDT - ENT - ATT&CK
T1574.011 - Services Registry Permissions Weakness - PER - ENT - ATT&CK
T1574.011 - Services Registry Permissions Weakness - PRI - ENT - ATT&CK
T1574.011 - Services Registry Permissions Weakness - NDT - ENT - ATT&CK
T1578.004 - Revert Cloud Instance - DEF - ENT - ATT&CK
T1573.001 - Symmetric Cryptography - C&C - ENT - ATT&CK
T1052.001 - Exfiltration over USB - EXF - ENT - ATT&CK
T1560.001 - Archive via Utility - EXF - ENT - ATT&CK
T1071.001 - Web Protocols - C&C - ENT - ATT&CK
T1224 - Assess leadership areas of interest - PDP - PRE - ATT&CK
T1225 - Identify gap areas - PDP - PRE - ATT&CK
T1226 - Conduct cost/benefit analysis - PDP - PRE - ATT&CK
T1227 - Develop KITs/KIQs - PDP - PRE - ATT&CK
T1228 - Assign KITs/KIQs into categories - PDP - PRE - ATT&CK
T1229 - Assess KITs/KIQs benefits - PDP - PRE - ATT&CK
T1230 - Derive intelligence requirements - PDP - PRE - ATT&CK
T1231 - Create strategic plan - PDP - PRE - ATT&CK
T1232 - Create implementation plan - PDP - PRE - ATT&CK
T1233 - Identify analyst level gaps - PDP - PRE - ATT&CK
T1234 - Generate analyst intelligence requirements - PDP - PRE - ATT&CK
T1235 - Receive operator KITs/KIQs tasking - PDP - PRE - ATT&CK
T1236 - Assess current holdings, needs, and wants - PDP - PRE - ATT&CK
T1237 - Submit KITs, KIQs, and intelligence requirements - PDD - PRE - ATT&CK
T1238 - Assign KITs, KIQs, and/or intelligence requirements - PDD - PRE - ATT&CK
T1239 - Receive KITs/KIQs and determine requirements - PDD - PRE - ATT&CK
T1240 - Task requirements - PDD - PRE - ATT&CK
T1241 - Determine strategic target - TAR - PRE - ATT&CK
T1242 - Determine operational element - TAR - PRE - ATT&CK
T1243 - Determine highest level tactical element - TAR - PRE - ATT&CK
T1244 - Determine secondary level tactical element - TAR - PRE - ATT&CK
T1245 - Determine approach/attack vector - TAR - PRE - ATT&CK
T1246 - Identify supply chains - TIG - PRE - ATT&CK
T1247 - Acquire OSINT data sets and information - TIG - PRE - ATT&CK
T1248 - Identify job postings and needs/gaps - TIG - PRE - ATT&CK
T1249 - Conduct social engineering - TIG - PRE - ATT&CK
T1250 - Determine domain and IP address space - TIG - PRE - ATT&CK
T1251 - Obtain domain/IP registration information - TIG - PRE - ATT&CK
T1252 - Map network topology - TIG - PRE - ATT&CK
T1253 - Conduct passive scanning - TIG - PRE - ATT&CK
T1254 - Conduct active scanning - TIG - PRE - ATT&CK
T1255 - Discover target logon/email address format - TIG - PRE - ATT&CK
T1256 - Identify web defensive services - TIG - PRE - ATT&CK
T1257 - Mine technical blogs/forums - TIG - PRE - ATT&CK
T1258 - Determine firmware version - TIG - PRE - ATT&CK
T1259 - Determine external network trust dependencies - TIG - PRE - ATT&CK
T1260 - Determine 3rd party infrastructure services - TIG - PRE - ATT&CK
T1261 - Enumerate externally facing software applications technologies, languages, and dependencies - TIG - PRE - ATT&CK
T1262 - Enumerate client configurations - TIG - PRE - ATT&CK
T1263 - Identify security defensive capabilities - TIG - PRE - ATT&CK
T1264 - Identify technology usage patterns - TIG - PRE - ATT&CK
T1265 - Identify supply chains - PIG - PRE - ATT&CK
T1266 - Acquire OSINT data sets and information - PIG - PRE - ATT&CK
T1267 - Identify job postings and needs/gaps - PIG - PRE - ATT&CK
T1268 - Conduct social engineering - PIG - PRE - ATT&CK
T1269 - Identify people of interest - PIG - PRE - ATT&CK
T1270 - Identify groups/roles - PIG - PRE - ATT&CK
T1271 - Identify personnel with an authority/privilege - PIG - PRE - ATT&CK
T1272 - Identify business relationships - PIG - PRE - ATT&CK
T1273 - Mine social media - PIG - PRE - ATT&CK
T1274 - Identify sensitive personnel information - PIG - PRE - ATT&CK
T1275 - Aggregate individual's digital footprint - PIG - PRE - ATT&CK
T1276 - Identify supply chains - OIG - PRE - ATT&CK
T1277 - Acquire OSINT data sets and information - OIG - PRE - ATT&CK
T1278 - Identify job postings and needs/gaps - OIG - PRE - ATT&CK
T1279 - Conduct social engineering - OIG - PRE - ATT&CK
T1280 - Identify business processes/tempo - OIG - PRE - ATT&CK
T1281 - Obtain templates/branding materials - OIG - PRE - ATT&CK
T1282 - Determine physical locations - OIG - PRE - ATT&CK
T1283 - Identify business relationships - OIG - PRE - ATT&CK
T1284 - Determine 3rd party infrastructure services - OIG - PRE - ATT&CK
T1285 - Determine centralization of IT management - OIG - PRE - ATT&CK
T1286 - Dumpster dive - OIG - PRE - ATT&CK
T1287 - Analyze data collected - TWI - PRE - ATT&CK
T1288 - Analyze architecture and configuration posture - TWI - PRE - ATT&CK
T1289 - Analyze organizational skillsets and deficiencies - TWI - PRE - ATT&CK
T1290 - Research visibility gap of security vendors - TWI - PRE - ATT&CK
T1291 - Research relevant vulnerabilities/CVEs - TWI - PRE - ATT&CK
T1292 - Test signature detection - TWI - PRE - ATT&CK
T1293 - Analyze application security posture - TWI - PRE - ATT&CK
T1294 - Analyze hardware/software security defensive capabilities - TWI - PRE - ATT&CK
T1295 - Analyze social and business relationships, interests, and affiliations - PWI - PRE - ATT&CK
T1296 - Assess targeting options - PWI - PRE - ATT&CK
T1297 - Analyze organizational skillsets and deficiencies - PWI - PRE - ATT&CK
T1298 - Assess vulnerability of 3rd party vendors - OWI - PRE - ATT&CK
T1299 - Assess opportunities created by business deals - OWI - PRE - ATT&CK
T1300 - Analyze organizational skillsets and deficiencies - OWI - PRE - ATT&CK
T1301 - Analyze business processes - OWI - PRE - ATT&CK
T1302 - Assess security posture of physical locations - OWI - PRE - ATT&CK
T1303 - Analyze presence of outsourced capabilities - OWI - PRE - ATT&CK
T1304 - Proxy/protocol relays - AOP - PRE - ATT&CK
T1305 - Private whois services - AOP - PRE - ATT&CK
T1306 - Anonymity services - AOP - PRE - ATT&CK
T1307 - Acquire and/or use 3rd party infrastructure services - AOP - PRE - ATT&CK
T1308 - Acquire and/or use 3rd party software services - AOP - PRE - ATT&CK
T1309 - Obfuscate infrastructure - AOP - PRE - ATT&CK
T1310 - Acquire or compromise 3rd party signing certificates - AOP - PRE - ATT&CK
T1311 - Dynamic DNS - AOP - PRE - ATT&CK
T1312 - Compromise 3rd party infrastructure to support delivery - AOP - PRE - ATT&CK
T1313 - Obfuscation or cryptography - AOP - PRE - ATT&CK
T1314 - Host-based hiding techniques - AOP - PRE - ATT&CK
T1315 - Network-based hiding techniques - AOP - PRE - ATT&CK
T1316 - Non-traditional or less attributable payment options - AOP - PRE - ATT&CK
T1317 - Secure and protect infrastructure - AOP - PRE - ATT&CK
T1318 - Obfuscate operational infrastructure - AOP - PRE - ATT&CK
T1319 - Obfuscate or encrypt code - AOP - PRE - ATT&CK
T1320 - Data Hiding - AOP - PRE - ATT&CK
T1321 - Common, high volume protocols and software - AOP - PRE - ATT&CK
T1322 - Misattributable credentials - AOP - PRE - ATT&CK
T1323 - Domain Generation Algorithms (DGA) - AOP - PRE - ATT&CK
T1324 - DNSCalc - AOP - PRE - ATT&CK
T1325 - Fast Flux DNS - AOP - PRE - ATT&CK
T1326 - Domain registration hijacking - EMI - PRE - ATT&CK
T1327 - Use multiple DNS infrastructures - EMI - PRE - ATT&CK
T1328 - Buy domain name - EMI - PRE - ATT&CK
T1329 - Acquire and/or use 3rd party infrastructure services - EMI - PRE - ATT&CK
T1330 - Acquire and/or use 3rd party software services - EMI - PRE - ATT&CK
T1331 - Obfuscate infrastructure - EMI - PRE - ATT&CK
T1332 - Acquire or compromise 3rd party signing certificates - EMI - PRE - ATT&CK
T1333 - Dynamic DNS - EMI - PRE - ATT&CK
T1334 - Compromise 3rd party infrastructure to support delivery - EMI - PRE - ATT&CK
T1335 - Procure required equipment and software - EMI - PRE - ATT&CK
T1336 - Install and configure hardware, network, and systems - EMI - PRE - ATT&CK
T1337 - SSL certificate acquisition for domain - EMI - PRE - ATT&CK
T1338 - SSL certificate acquisition for trust breaking - EMI - PRE - ATT&CK
T1339 - Create backup infrastructure - EMI - PRE - ATT&CK
T1340 - Shadow DNS - EMI - PRE - ATT&CK
T1341 - Build social network persona - PDV - PRE - ATT&CK
T1342 - Develop social network persona digital footprint - PDV - PRE - ATT&CK
T1343 - Choose pre-compromised persona and affiliated accounts - PDV - PRE - ATT&CK
T1344 - Friend/Follow/Connect to targets of interest - PDV - PRE - ATT&CK
T1345 - Create custom payloads - BDC - PRE - ATT&CK
T1346 - Obtain/re-use payloads - BDC - PRE - ATT&CK
T1347 - Build and configure delivery systems - BDC - PRE - ATT&CK
T1348 - Identify resources required to build capabilities - BDC - PRE - ATT&CK
T1349 - Build or acquire exploits - BDC - PRE - ATT&CK
T1350 - Discover new exploits and monitor exploit-provider forums - BDC - PRE - ATT&CK
T1351 - Remote access tool development - BDC - PRE - ATT&CK
T1352 - C2 protocol development - BDC - PRE - ATT&CK
T1353 - Post compromise tool development - BDC - PRE - ATT&CK
T1354 - Compromise 3rd party or closed-source vulnerability/exploit information - BDC - PRE - ATT&CK
T1355 - Create infected removable media - BDC - PRE - ATT&CK
T1356 - Test callback functionality - TST - PRE - ATT&CK
T1357 - Test malware in various execution environments - TST - PRE - ATT&CK
T1358 - Review logs and residual traces - TST - PRE - ATT&CK
T1359 - Test malware to evade detection - TST - PRE - ATT&CK
T1360 - Test physical access - TST - PRE - ATT&CK
T1361 - Test signature detection for file upload/email filters - TST - PRE - ATT&CK
T1362 - Upload, install, and configure software/tools - STG - PRE - ATT&CK
T1363 - Port redirector - STG - PRE - ATT&CK
T1364 - Friend/Follow/Connect to targets of interest - STG - PRE - ATT&CK
T1365 - Hardware or software supply chain implant - STG - PRE - ATT&CK
T1366 - Targeted social media phishing - LNC - PRE - ATT&CK
T1367 - Spear phishing messages with malicious attachments - LNC - PRE - ATT&CK
T1368 - Spear phishing messages with text only - LNC - PRE - ATT&CK
T1369 - Spear phishing messages with malicious links - LNC - PRE - ATT&CK
T1370 - Untargeted client-side exploitation - LNC - PRE - ATT&CK
T1371 - Targeted client-side exploitation - LNC - PRE - ATT&CK
T1372 - Unconditional client-side exploitation/Injected Website/Driveby - LNC - PRE - ATT&CK
T1373 - Push-notification client-side exploit - LNC - PRE - ATT&CK
T1374 - Credential pharming - LNC - PRE - ATT&CK
T1375 - Leverage compromised 3rd party resources - LNC - PRE - ATT&CK
T1376 - Conduct social engineering or HUMINT operation - LNC - PRE - ATT&CK
T1377 - Exploit public-facing application - LNC - PRE - ATT&CK
T1378 - Replace legitimate binary with malware - LNC - PRE - ATT&CK
T1379 - Disseminate removable media - STG - PRE - ATT&CK
T1380 - Deploy exploit using advertising - LNC - PRE - ATT&CK
T1381 - Authentication attempt - LNC - PRE - ATT&CK
T1382 - DNS poisoning - LNC - PRE - ATT&CK
T1383 - Confirmation of launched compromise achieved - COM - PRE - ATT&CK
T1384 - Automated system performs requested action - COM - PRE - ATT&CK
T1385 - Human performs requested action of physical nature - COM - PRE - ATT&CK
T1386 - Authorized user performs requested cyber action - COM - PRE - ATT&CK
T1387 - Unauthorized user introduces compromise delivery mechanism - COM - PRE - ATT&CK
T1388 - Compromise of externally facing system - COM - PRE - ATT&CK
T1389 - Identify vulnerabilities in third-party software libraries - TWI - PRE - ATT&CK
T1390 - OS-vendor provided communication channels - AOP - PRE - ATT&CK
T1391 - Choose pre-compromised mobile app developer account credentials or signing keys - PDV - PRE - ATT&CK
T1392 - Obtain Apple iOS enterprise distribution key pair and certificate - PDV - PRE - ATT&CK
T1393 - Test ability to evade automated mobile application security analysis performed by app stores - TST - PRE - ATT&CK
T1394 - Distribute malicious software development tools - STG - PRE - ATT&CK
T1395 - Runtime code download and execution - LNC - PRE - ATT&CK
T1396 - Obtain booter/stressor subscription - EMI - PRE - ATT&CK
T1397 - Spearphishing for Information - TIG - PRE - ATT&CK"""
MITRE_ATTACK_TAGS_SPLIT = MITRE_ATTACK_TAGS.split('\n')
MITRE_ATTACK_TACTIC_ABBREVIATIONS = {
    'adversaryopsec': 'AOP',
    'buildcapabilities': 'BDC',
    'collection': 'COL',
    'commandandcontrol': 'C&C',
    'compromise': 'COM',
    'credentialaccess': 'CRA',
    'defenseevasion': 'DEF',
    'discovery': 'DIS',
    'establish&maintaininfrastructure': 'EMI',
    'execution': 'EXE',
    'exfiltration': 'EXF',
    'impact': 'IMP',
    'initialaccess': 'INI',
    'lateralmovement': 'LAT',
    'launch': 'LNC',
    'organizationalinformationgathering': 'OIG',
    'organizationalweaknessidentification': 'OWI',
    'peopleinformationgathering': 'PIG',
    'peopleweaknessidentification': 'PWI',
    'persistence': 'PER',
    'personadevelopment': 'PDV',
    'prioritydefinitiondirection': 'PDD',
    'prioritydefinitionplanning': 'PDP',
    'privilegeescalation': 'PRI',
    'stagecapabilities': 'STG',
    'targetselection': 'TAR',
    'technicalinformationgathering': 'TIG',
    'technicalweaknessidentification': 'TWI',
    'testcapabilities': 'TST',
    'unknown': 'NDT',
}


class MitreAttackUtils:
    """TcEx framework Mitre Attacks Utils class"""

    @staticmethod
    def technique_id_to_tags(technique_id: str, include_ndt_tag: bool = False) -> List[str]:
        """Return the ThreatConnect tags for the given technique_id."""
        matching_tags = []
        technique_id_prefix = f'{technique_id.title()} -'
        for tag in MITRE_ATTACK_TAGS_SPLIT:
            if tag.startswith(technique_id_prefix):
                is_ndt_tag = '- NDT - ' in tag
                if include_ndt_tag or not is_ndt_tag:
                    matching_tags.append(tag)

        return matching_tags

    @staticmethod
    def tactic_name_abbreviation(tactic_name: str):
        """Return the ThreatConnect abbreviation for the given tactic_name."""
        tactic_name = tactic_name.replace(' ', '').replace('-', '').lower()
        return MITRE_ATTACK_TACTIC_ABBREVIATIONS.get(tactic_name)
