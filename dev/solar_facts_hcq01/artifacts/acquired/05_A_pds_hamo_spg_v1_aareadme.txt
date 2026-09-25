PDS_VERSION_ID       = PDS3                                                   
RECORD_TYPE          = STREAM                                                 
                                                                              
^TEXT                = "AAREADME.TXT"                                         
OBJECT               = TEXT                                                   
  PUBLICATION_DATE   = 2016-09-01                                             
  NOTE               = "AAREADME.TXT describes this volume."                  
END_OBJECT           = TEXT                                                   
END                                                                           
                                                                              
                              Volume DWNCHSPG_2                               
             Dawn FC2 Ceres Encounter HAMO Digital Terrain Model (DTM) SPG    
                                                                              
                                  Data Set                                    
                     DAWN-A-FC2-5-CERESHAMODTMSPG-V1.0                        
                                                                              
==============================================================================
                         Brief Disk Description                               
==============================================================================
      This volume contains the Ceres digital terrain model (DTM) based on     
      the Dawn High Altitude Mapping orbit (HAMO) Framing Camera 2 (FC2)      
      images and derived by using the stereo photogrammetry (SPG) method. The 
      HAMO DTM covers approximately 98% of Ceres’ surface (few permanently    
      shadowed areas near the poles required interpolation). The a DTM has    
      a lateral spacing of ~136.7 m/pixel (60 pixel/degree) and a vertical    
      accuracy of about 10 m. A global DTM is provided in  an equidistant     
      cylindrical projection and hemispheric DTMs are provided for both       
      polar regions as stereographic projections. The DTMs are formatted as   
      images where the DN values give the height in meters above a reference  
      sphere of 470.0 km.                                                     
                                                                              
      Dawn mission is equipped with two identical framing cameras (FC1 & FC2) 
      [SIERKSETAL2011] which have one clear filter and seven band pass        
      filters. At Ceres, only the FC2 was used to acquire science images      
      while the FC1 was held in reserve. Clear filter images which were       
      taken during HAMO were used to produce a global DTM of the              
      illuminated part of Ceres [PREUSKERETAL2016]. Dawn orbited Ceres        
      during in 6 cycles between August 16 and October 23, 2015 at the        
      HAMO altitude of ~1475 km. A cycle is a single complete mapping of      
      surface at a fixed attitude (nadir or off-nadir). The framing camera    
      acquired about 2350 clear filter images [PREUSKERETAL2016] during the   
      HAMO phase. The images were taken with different viewing angles and     
      similar illumination conditions by slewing the spacecraft to various    
      off-nadir attitudes. These images are analyzed by using the SPG method  
      [PREUSKERETAL2016] to produce the Ceres HAMO DTM.                       
                                                                              
                                                                              
NOTE: Reading the Science Plan (DOCUMENTS/SCIENCE_PLAN/DAWN_SCIPLAN_V5_4.PDF) 
      is critical to the understanding of the planned Ceres observations and  
      science objectives.  The calibration procedure and files are identical  
      to those applied to the Vesta data.                                     
                                                                              
      There are several key publications that describe the data processing    
      and image mosaicking. These include:                                    
                                                                              
      PREUSKERETAL2016                                                        
        Preusker,F.,Scholten,F.,Matz,K.-D.,Elgner,S.,Jaumann,R.,Roatsch,T.,   
        Joy,S.P.,Polanskey,C.A.,Raymond,C.A.,Russell,C.T.,2016.Dawn at Ceres  
        - Shape model and rotational state, 47th Lunar and Planetary Science  
        Conference (LPSC) - USRA-Houston, 2016 , Abstract 1954.               
        http://www.hou.usra.edu/meetings/lpsc2016/pdf/1954.pdf                
                                                                              
      ROATSCHETAL2016                                                         
        Roatsch,T., E. Kersten,K.-D. Matz,F. Preusker, F. Scholten,           
        R. Jaumann,C.A. Raymond, C.T.Russell, High-resolution Ceres High      
        Altitude Mapping Orbit Atlas derived from Dawn Framing Camera images, 
        Planetary and Space Sciences, in press, 2016.                         
                                                                              
      PREUSKERETAL2012                                                        
        Preusker, F., J. Oberst, J. Head, T. Watters, M. Robinson,            
        M. Zuber, S. Solomon, Stereo topographic models of Mercury            
        after three MESSENGER flybys. Planet. Space Sci. (2011).              
        DOI:10.1016/j.pss.2011.07.005                                         
                                                                              
      RAYMONDETAL2012                                                         
        Raymond, C.A., R. Jaumann, A. Nathues, H. Sierks, T. Roatsch,         
        F. Preusker, F. Scholten, R.W. Gaskell, L. Jorda, H.-U. Keller,       
        M.T. Zuber, D.E. Smith, N. Mastrodemos, and S. Mottola,               
        The Dawn topography investigation. Space Sci. Rev. 163, 487 (2011).   
        DOI: 10.1007/s11214-011-9863-z                                        
                                                                              
     /DOCUMENT/STEREO_PHOTOGRAMMETRY.PDF (this volume)                        
                                                                              
     POLANSKEYETAL2016                                                        
        Polanskey, C., S. Joy, and C. Raymond, "Dawn Ceres Mission: Science   
        Operations Performance", SpaceOps 2016 Conference, SpaceOps           
        Conferences, (in press).                                              
                                                                              
                                                                              
                                                                              
All data are stored in the 'DATA' branch of the directory tree. In addition   
to the data files, ancillary information is stored in an attached PDS label.  
                                                                              
Additional copies of the data in TIFF (Tagged Image File Format)format can    
be found in the EXTRAS directory of this volume. Some users may find this     
format easier to work with in some software packages such as ArcGIS.          
                                                                              
Users of these data are encouraged to acknowledge both the PDS and the        
principal investigators of the instruments whose data is used in analysis     
in all publications.                                                          
                                                                              
==============================================================================
File Naming Conventions                                                       
==============================================================================
Data and browse images on this volume conform to the following naming         
convention:                                                                   
                                                                              
    CE_PHASE_T_LAT_LONG_PROJ_TYPE.EXT                                         
                                                                              
where:                                                                        
    CE_HAMO_G is literal for Ceres HAMO Global                                
    LAT       is the center latitude of the image                             
    LONG      is the center longitude of the image                            
    PROJ      is the map projection type (CYL=cylindrical, STE=stereographic  
    DTM       is literal, the image type is DTM,                              
example:                                                                      
    CE_HAMO_G_00N_180E_EQU_DTM.IMG                                            
       Ceres HAMO global centered at 0N latitude, 108E longitude using a      
       equidistant cyclindrical projection for the DTM.                       
                                                                              
                                                                              
==============================================================================
Volume Set Information                                                        
==============================================================================
                                                                              
This volume is part of the FC2 high level data volume set. This volume set    
includes the following volumes:                                               
                                                                              
    Volume ID     Description                                                 
    ------------------------------------------------------------              
    DWNVFC2_2     Dawn FC2 L2/3 Vesta Encounter mosaics                       
    DWNVSPG_2     Dawn FC2 L2/L3 Vesta stereo-photogrammetric DTM             
    DWNVSPC_2     Dawn FC2 L2/L3 Vesta stereo-photoclinometric DTM            
    DWNCHCFC2_2   Dawn FC2 L2/3 Ceres HAMO clear mosaics                      
    DWNCHFFC2_2   Dawn FC2 L2/3 Ceres HAMO color filter mosaics               
    DWNCLCFC2_2   Dawn FC2 L2/3 Ceres LAMO clear mosaics                      
    DWNCHSPG_2    Dawn FC2 L2/L3 Ceres HAMO stereo-photogrammetric DTM        
    DWNCHSPC_2    Dawn FC2 L2/L3 Ceres HAMO stereo-photoclinometric DTM       
    DWNCLSPG_2    Dawn FC2 L2/L3 Ceres LAMO stereo-photogrammetric DTM        
    DWNCLSPC_2    Dawn FC2 L2/L3 Ceres LAMO stereo-photoclinometric DTM       
                                                                              
==============================================================================
Mission Facts                                                                 
==============================================================================
                                                                              
The 'Dawn Ceres Science Phases' table below provides a list Dawn Ceres        
Encounter mission phase start dates.                                          
                                                                              
                                                                              
------------------------------------------------------------------------------
Dawn Ceres Science Phases                                                     
------------------------------------------------------------------------------
start date (DOY)   Phase Name (ID)                                            
------------------------------------------------------------------------------
2014-12-26 (360)    CERES SCIENCE APPROACH (CSA)                              
2015-04-24 (114)    CERES SCIENCE ROTATIONAL CHARACTERIZATION 3 (CSR)         
2015-05-09 (129)    CERES TRANSFER TO SURVEY (CTS)                            
2015-06-04 (155)    CERES SCIENCE SURVEY (CSS)                                
2015-07-01 (182)    CERES TRANSFER TO HAMO (CTH)                              
2015-08-17 (228)    CERES SCIENCE HAMO (CSH)                                  
2015-10-23 (296)    CERES TRANSFER TO LAMO (CTL)                              
2015-12-16 (350)    CERES SCIENCE LAMO (CSL)                                  
2016-06-19 (171)    End of prime mission                                      
------------------------------------------------------------------------------
                                                                              
                                                                              
==============================================================================
File Formats                                                                  
==============================================================================
                                                                              
The data files on this volume are formatted as PDS images (.IMG, binary)      
with attached PDS3 labels. The PDS label contains information                 
describing spacecraft, target, and data record format. Even though the PDS    
labels are attached to the files, they can be viewed in a text editor.        
                                                                              
A data set description, instrument description, and other PDS documents       
are in .CAT files in the /CATALOG directory.                                  
                                                                              
Additional documentation is generally located in the DOCUMENT directory.      
                                                                              
Note for Windows users:                                                       
In more recent versions of the Microsoft Windows operating system the .CAT by 
default is reserved as 'Security Catalog.'  The .CAT files contained in       
this volume are ASCII text files, and can be read by any form of text editor. 
To make Windows open files with this name extension as text files, do the     
following. To make Windows open files with this name extension as text files  
right click the .CAT file, select with and choose a text editor to open the   
file.                                                                         
                                                                              
                                                                              
==============================================================================
Errata                                                                        
==============================================================================
                                                                              
Every effort has been made to insure that the data and documentation are of   
the best possible quality. However, mistakes are inevitable. There is a file  
called ERRATA.TXT found at the root level of this volume which contains a list
of known deficiencies or caveats associated with data on this volume at the   
time this volume was produced.                                                
                                                                              
                                                                              
==============================================================================
Volume Contents and Structure                                                 
==============================================================================
                                                                              
This section describes the volume structure and naming conventions. Below is  
a tree diagram of the volume, followed by a description of the directory      
function and key files in each directory.                                     
                                                                              
 DWNCHSPG_2 (root directory)                                                  
   |                                                                          
   |- AAREADME.TXT  Describes volume contents, and organization (this file)   
   |                                                                          
   |- ERRATA.TXT    Describes known deficiencies or caveats in the data or    
   |                on this volume.                                           
   |                                                                          
   |- VOLDESC.CAT   High level description of volume contents.                
   |                                                                          
   |- [BROWSE]   Contains a JPG images of the data located in the DATA branch 
   |             of this volume. More information on the contents of this     
   |             directory is provided in the file /BROWSE/BROWINFO.TXT.      
   |                                                                          
   |- [CATALOG]  PDS catalog files containing information describing the      
   |             data, instrument, instrument personnel, relevant references, 
   |             the spacecraft, and mission. More information on the contents
   |             of this directory is provided in the file                    
   |             /CATALOG/CATINFO.TXT.                                        
   |                                                                          
   |- [DATA]     Contains the data files.                                     
   |                                                                          
   |- [DOCUMENT] Contains documents describing the instrument, and data       
   |             acquisition, processing, and usage. More information on the  
   |             contents of this directory is provided in the file           
   |             /DOCUMENT/DOCINFO.TXT.                                       
   |                                                                          
   |- [EXTRAS]   Contains files which facilitate the use of the data on the   
   |             disk, but which are not actually required for the use or     
   |             understanding of those data. A more detailed description of  
   |             the contents of this directory is provided in the file       
   |             /EXTRAS/EXTRINFO.TXT.                                        
   |                                                                          
   |- [GEOMETRY] Contains a SPICE planetary contants kernel (PCK) that is     
   |             consistent with the DTM model being archived.                
   |                                                                          
   |- [INDEX]    Contains a table of contents for all files located on this   
   |             volume, and the volume set to date. A more detailed          
   |             description of the contents of this directory is provided in 
   |             the file /INDEX/INDXINFO.TXT.                                
                                                                              
                                                                              
============================================================================  
Contacts                                                                      
============================================================================  
                                                                              
This volume was produced for the Planetary Data System (PDS) at the Small     
Bodies node. The data, and associated metadata were supplied by Dr. Thomas    
Roatsch, DLR Berlin-Adlershof. The volume was assembled at the Dawn Science   
Center (DSC), by Joseph N. Mafi.                                              
                                                                              
For questions or problems regarding the volume, please contact Carol Neese    
at the PDS Small Bodies Node:                                                 
                                                                              
  Email             neese@psi.edu                                             
  Telephone         520-622-6300                                              
  Mail              Carol Neese                                               
                    Planetary Science Institute                               
                    1700 E. Ft. Lowell, Ste. 106                              
                    Tuscon, AZ 85719-2395                                     
                    USA                                                       
                                                                              
For question regarding the data, please contact Dr. Thomas Roatsch of DLR:    
                                                                              
  Email             thomas.roatsch@dlr.de                                     
  Telephone         +49 30 67055-0                                            
  Mail              DLR Berlin-Adlershof                                      
                    RutherfordstraBe 2                                        
                    12489 Berlin                                              
                    Germany                                                   
                                                                              
For questions regarding PDS Standards or other archives available from the    
PDS, please contact PDS Operator at the PDS Engineering Node (at JPL):        
                                                                              
  Email             pds_operator@jpl.nasa.gov                                 
  Telephone         818-354-4321                                              
  Mail              Planetary Data System, PDS Operator                       
                    Jet Propulsion Laboratory                                 
                    Mail Stop 202-101                                         
                    4800 Oak Grove Dr.                                        
                    Pasadena, CA 91109-8099                                   
                    USA                                                       
                                                                              
The PDS assumes no legal liability for errors on this disk. All users are     
encouraged to verify the correctness of the data prior to submitting any      
publications or other work based on these data. Please report errors on this  
disk to the Small Bodies Node of the PDS through the ERRATA reporting         
procedures described above.                                                   
