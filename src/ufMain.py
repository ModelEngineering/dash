import os, sys
from delphifmx import *
import requests
import json
import tempfile
import h5py
import numpy as np
import time
import pathlib

class frmMain(Form):

    def __init__(self, owner):
        self.Layout1 = None
        self.Layout2 = None
        self.Layout3 = None
        self.Layout4 = None
        self.listBoxProjects = None
        self.Splitter1 = None
        self.Layout5 = None
        self.listBoxFiles = None
        self.moDisplay = None
        self.btnGetProjects = None
        self.LabelProject = None     
        self.imageControl = None  
        self.pnlProjectButtons = None
        self.btnGetProjectDetails = None  
        self.lblMessage = None       
        self.LoadProps(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ufMain.pyfmx"))
        self.exePath = os.path.dirname(sys.argv[0])
        #self.__sm = StyleManager() 
        #self.__sm.SetStyle(StyleStreaming().LoadFromFile(self.exePath + "\\" + "Air.style"))
        self.connectEvents()
        self.projects = None     
        self.fileNameUrls = {}  
        self.selectedProjectIndex = -1
    
    def connectEvents (self):
        self.btnGetProjects.OnClick = self.btnGetProjectsClick
        self.listBoxProjects.OnChange = self.listBoxProjectsClick
        self.listBoxFiles.OnChange = self.listBoxFilesClick
        self.btnGetProjectDetails.OnClick = self.getDetailsClick
        self.moDisplay.WordWrap = True
        self.lblMessage.text = ''
        #self.btnRunSim.OnClick = self.btnRunSimClick
        #self.moDisplay.WordWrap = True
        self.api_url = "https://api.biosimulations.org/"
      
      
    def getProjectIdswithCitations (self, Sender):
        response = requests.get(self.api_url + 'projects')
        self.projects = response.json()  
        for obj in self.projects:
            response = requests.get(self.api_url + 'files/' + obj['simulationRun'])
                         
      
    def findProjectSimId (self, projectId):
        if self.projects != None:
           if self.listBoxProjects.ItemIndex != -1:
              for obj in self.projects:
                 for obj in self.projects:
                    if obj['id'] == self.listBoxProjects.Items[self.listBoxProjects.ItemIndex]: 
                        return obj['simulationRun']
           else:
              return ''
        else:
            return ''
                              
              
    def btnGetProjectsClick(self, Sender):
        self.lblMessage.text = ''
        response = requests.get(self.api_url + 'projects')
        self.projects = response.json()
        self.listBoxProjects.Items.BeginUpdate()
        for obj in self.projects:
            self.listBoxProjects.Items.Add (obj['id'])
        self.listBoxProjects.Items.EndUpdate()        
    
    
    def listBoxProjectsClick (self, Sender):
        self.lblMessage.text += '1'
        index = self.listBoxProjects.ItemIndex
        if index == -1:
           self.lblMessage.text += "Nothing has been selected"
           return None
        else:  
           self.selectedProjectIndex = index 
           self.lblMessage.text = str (self.selectedProjectIndex)
           self.LabelProject.text = self.listBoxProjects.Items[index]
           self.moDisplay.Lines.Clear()
            
           self.listBoxFiles.Clear()
           self.fileNameUrls = {}
           simId = self.findProjectSimId (index)
           #if simId == '':  # Add error check here          
          
           response = requests.get(self.api_url + 'files/' + simId)
           for report in response.json():
               url = report['url']
               fileName = os.path.basename(url)
               self.fileNameUrls[fileName] = url
               self.listBoxFiles.Items.Add (fileName)                          
               
               
    def listBoxFilesClick (self, Sender):
        self.lblMessage.text  = self.selectedProjectIndex
        if self.selectedProjectIndex == -1:
           self.lblMessage.text = "Get the projects and select one project"
           return None
    
        fileName = self.listBoxFiles.Items[self.listBoxFiles.ItemIndex]
        file_extension = pathlib.Path(fileName).suffix
        self.moDisplay.text = file_extension
        if file_extension in ['.sedml', '.cellml', '.rdf', '.xml', '.json', '.txt', '.ode', '.html']:
            r = requests.get(self.fileNameUrls[fileName])
            self.moDisplay.Lines.Add(r.content.decode())
            self.moDisplay.Repaint()
        if file_extension == '.png':
            r = requests.get(self.fileNameUrls[fileName])
            self.moDisplay.text == r
        if file_extension in ['.jpg', '.png']:  
           r = requests.get(self.fileNameUrls[fileName])
           self.moDisplay.Lines.Add (type (r.content))
           bs = BytesStream(bytearray(bytearray (r.content)))
           self.moDisplay.Lines.Add (type (bs))    
                       
           self.imageControl.Bitmap.LoadFromStream (bs)                     
                  
    def getDetailsClick (self, Sender):
        if self.selectedProjectIndex == -1:
           self.lblMessage.text = "Get the projects and select one project"
           return
               
        index = self.selectedProjectIndex
   
        self.moDisplay.Lines.Clear()      
        simId = self.findProjectSimId (index)  
        self.moDisplay.text = 'simulationRun Id: ' + simId
        r = self.api_url + 'runs/' + simId + '/summary'
        response = requests.get(r)
        metadata = response.json()['metadata']
        txt = metadata[0]['abstract']
        
        self.moDisplay.Lines.Add ('')
        self.moDisplay.Lines.Add ('Abstract')
        self.moDisplay.Lines.Add (txt)        
        self.moDisplay.Lines.Add ('')
        
        txt = metadata[0]['description']        
        self.moDisplay.Lines.Add ('Description')
        self.moDisplay.Lines.Add (txt)               
    
def main():
    Application.Initialize()
    Application.Title = 'Biosimulations Browser'
    Application.MainForm = frmMain(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
