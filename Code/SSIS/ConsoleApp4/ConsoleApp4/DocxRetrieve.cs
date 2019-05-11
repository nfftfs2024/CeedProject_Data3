using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using Microsoft.SharePoint.Client;
using System.Security;
using System.Net;

namespace DocxRetrieve
{
    class DocxRetrieve
    {
        static void Main(string[] args)
        {
            // Starting with ClientContext, the constructor requires a URL to the 
            // server running SharePoint. 
            //ClientContext context = new ClientContext("http://staffnet13.data3.com.au");
            //string siteCollectionUrl = "https://staffnet13.data3.com.au/processes/cs/cas/";
            string siteCollectionUrl = "http://d3test13.data3.com.au/d3process/cs/cas/";
            string userName = "James_Chou@data3.com.au";
            string password = "P@ssword1";
            string listTitle = "Documents";
            string filePath = "D:\\DOC";

            // Delete all files in the local directory
            System.IO.DirectoryInfo di = new DirectoryInfo(filePath);
            foreach (FileInfo file in di.GetFiles())
            {
                file.Delete();
            }

            ClientContext ctx = new ClientContext(siteCollectionUrl);
            NetworkCredential userCredentials = new NetworkCredential(userName, password);
            ctx.Credentials = userCredentials;
            //ConnectToSharePointOnline();
            DownloadAllFilesFromDocLib( ctx, listTitle , filePath);
        }
        //public static void ConnectToSharePointOnline()
        //{
        //    string siteCollectionUrl = "https://staffnet13.data3.com.au/processes/cs/cas/";
        //    string userName = "James_Chou@data3.com.au";
        //    string password = "P@ssword1";
        //    string listTitle = "Pages";
        //    string filePath = "D:\\Desktop\\New folder";

        //    // Namespace: Microsoft.SharePoint.Client  
        //    ClientContext ctx = new ClientContext(siteCollectionUrl);

        //    // Namespace: System.Security
        //    //SecureString secureString = new SecureString();
        //    //password.ToList().ForEach(secureString.AppendChar);

        //    // Namespace: Microsoft.SharePoint.Client  
        //    //ctx.Credentials = new SharePointOnlineCredentials(userName, secureString);

        //    // Namespace: Microsoft.SharePoint.Client  
        //    //Site site = ctx.Site;
        //    NetworkCredential userCredentials = new NetworkCredential(userName, password);
        //    ctx.Credentials = userCredentials;
        //    ctx.ExecuteQuery();

        //    //ctx.Load(site);
        //    //ctx.ExecuteQuery();
        //    List ss = ctx.Web.Lists.GetByTitle(listTitle);
        //    //var listItem = list.GetItems(list);
        //    ctx.Load(ss);
        //    ctx.ExecuteQuery();
        //    if (ss != null && ss.ItemCount > 0)
        //    {
        //        Microsoft.SharePoint.Client.CamlQuery camlQuery = new CamlQuery();
        //        camlQuery.ViewXml =
        //           @"<View Scope='RecursiveAll'>  
        //        <Query> 
        //           <Where><Eq><FieldRef Name='FSObjType' /><Value Type='Integer'>0</Value></Eq></Where> 
        //        </Query> 
        //         <ViewFields><FieldRef Name='FileLeafRef' /></ViewFields> 
        //  </View>";

        //        ListItemCollection listItems = ss.GetItems(camlQuery);
        //        ctx.Load(listItems);
        //        ctx.ExecuteQuery();

        //        foreach (var item in listItems)
        //        {
        //            Console.WriteLine(item.FieldValues["FileLeafRef"]);
        //        }
        //        Console.WriteLine("yeby");
        //        Console.ReadKey();
        //    }
        //}

        public static void DownloadAllFilesFromDocLib(ClientContext context, string docLibName, string path)
        {
            if (!path.EndsWith("\\"))
            {
                path = path + "\\";
            }
            //Web web = context.Site.RootWeb;

            List doclib = context.Web.Lists.GetByTitle(docLibName);

            context.Load(doclib);

            //context.Load(web);
            context.ExecuteQuery();

            FileCollection filesInRootFolder = doclib.RootFolder.Files;
            //FolderCollection subfolders = doclib.RootFolder.Folders;
            context.Load(filesInRootFolder);
            //context.Load(subfolders);
            context.ExecuteQuery();

            //download files from root folders
            foreach (Microsoft.SharePoint.Client.File file in filesInRootFolder)
            {
                FileInformation fileInfo = Microsoft.SharePoint.Client.File.OpenBinaryDirect(context, file.ServerRelativeUrl);   
                var clientResultStream = file.OpenBinaryStream();
                context.ExecuteQuery();
                var stream = clientResultStream.Value;
                System.IO.Stream fileOutputStream = stream;
                System.IO.Stream fileInputputStream = new FileStream(path + file.Name, FileMode.OpenOrCreate, FileAccess.ReadWrite);
                Console.WriteLine(path + file.Name + "GOGOGOG!");
                byte[] bufferByte = new byte[1024 * 100];

                int len = 0;
                while ((len = fileOutputStream.Read(bufferByte, 0, bufferByte.Length)) > 0)
                {
                    fileInputputStream.Write(bufferByte, 0, len);
                    fileInputputStream.Flush();
                }
                fileInputputStream.Close();
                fileOutputStream.Close();

            }
        }


        }
}
