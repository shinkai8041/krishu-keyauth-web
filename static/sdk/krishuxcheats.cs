/**
 * Krishu X Cheats — High-Performance Zero-Dependency C# SDK
 * 
 * Works out-of-the-box in:
 * - .NET Framework 4.5, 4.6, 4.7.2, 4.8, 4.8.1
 * - .NET Core 2.x, 3.x
 * - .NET 5, 6, 7, 8, 9, 10
 * - Windows Forms, WPF, Console, Unity
 * 
 * NO EXTERNAL NUGET PACKAGES REQUIRED!
 */

#pragma warning disable CS8981, SYSLIB0014, CA1416
using System;
using System.IO;
using System.Net;
using System.Text;
using System.Security.Principal;
using Microsoft.Win32;

namespace KrishuXCheats
{
    public class api
    {
        public string name { get; set; }
        public string ownerid { get; set; }
        public string secret { get; set; }
        public string version { get; set; }
        public string apiUrl { get; set; }

        public Response response { get; private set; }
        public UserData user_data { get; private set; }
        public AppData app_data { get; private set; }

        private bool isInitialized = false;

        public api(string name, string ownerid, string secret, string version, string apiUrl = "https://krishu-keyauth-web.onrender.com/api/v1")
        {
            this.name = name ?? string.Empty;
            this.ownerid = ownerid ?? string.Empty;
            this.secret = secret ?? string.Empty;
            this.version = version ?? "1.0.0";
            this.apiUrl = (apiUrl ?? "http://localhost:3000/api/v1").TrimEnd('/');

            this.response = new Response();
            this.user_data = new UserData();
            this.app_data = new AppData();

            try
            {
                // Enable TLS 1.2 for modern secure web endpoints
                ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072 | SecurityProtocolType.Tls;
            }
            catch { }
        }

        public static string getHWID()
        {
            try
            {
                using (RegistryKey key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\Microsoft\Cryptography"))
                {
                    if (key != null)
                    {
                        object guid = key.GetValue("MachineGuid");
                        if (guid != null && !string.IsNullOrEmpty(guid.ToString()))
                            return guid.ToString();
                    }
                }
            }
            catch { }

            try
            {
                var id = WindowsIdentity.GetCurrent();
                if (id != null && id.User != null && !string.IsNullOrEmpty(id.User.Value))
                    return id.User.Value;
            }
            catch { }

            return Environment.MachineName + "-" + Environment.UserName;
        }

        public void init()
        {
            try
            {
                string payload = string.Format(
                    "{{\"name\":\"{0}\",\"ownerid\":\"{1}\",\"secret\":\"{2}\",\"version\":\"{3}\"}}",
                    Escape(this.name), Escape(this.ownerid), Escape(this.secret), Escape(this.version)
                );

                string res = PostRequest("/init", payload);
                bool succ = GetBool(res, "success");
                string msg = GetString(res, "message");

                response.success = succ;
                response.message = !string.IsNullOrEmpty(msg) ? msg : (succ ? "Initialized" : "Init failed");

                if (succ)
                {
                    isInitialized = true;
                    app_data.name = GetString(res, "name");
                    app_data.version = GetString(res, "version");
                    app_data.announcement = GetString(res, "announcement");
                    app_data.downloadUrl = GetString(res, "downloadUrl");
                }
            }
            catch (Exception ex)
            {
                response.success = false;
                response.message = "Init error: " + ex.Message;
            }
        }

        public void login(string username, string password)
        {
            if (!isInitialized)
            {
                init();
                if (!response.success) return;
            }

            try
            {
                string hwid = getHWID();
                string payload = string.Format(
                    "{{\"name\":\"{0}\",\"ownerid\":\"{1}\",\"secret\":\"{2}\",\"username\":\"{3}\",\"password\":\"{4}\",\"hwid\":\"{5}\"}}",
                    Escape(this.name), Escape(this.ownerid), Escape(this.secret),
                    Escape(username), Escape(password), Escape(hwid)
                );

                string res = PostRequest("/login", payload);
                bool succ = GetBool(res, "success");
                string msg = GetString(res, "message");

                response.success = succ;
                response.message = !string.IsNullOrEmpty(msg) ? msg : (succ ? "Login successful" : "Login failed");

                if (succ)
                {
                    user_data.username = GetString(res, "username");
                    user_data.level = GetString(res, "level");
                    user_data.expires = GetString(res, "expiresAt");
                    if (string.IsNullOrEmpty(user_data.expires) || user_data.expires == "null")
                        user_data.expires = "Lifetime";

                    user_data.lifetime = GetBool(res, "lifetime") || user_data.expires == "Lifetime";
                    user_data.hwid = GetString(res, "hwid");
                    user_data.token = GetString(res, "token");
                }
            }
            catch (Exception ex)
            {
                response.success = false;
                response.message = "Login error: " + ex.Message;
            }
        }

        public void register(string username, string password, string licenseKey)
        {
            if (!isInitialized)
            {
                response.success = false;
                response.message = "Please initialize API before calling register()";
                return;
            }

            try
            {
                string hwid = getHWID();
                string payload = string.Format(
                    "{{\"name\":\"{0}\",\"ownerid\":\"{1}\",\"secret\":\"{2}\",\"username\":\"{3}\",\"password\":\"{4}\",\"licenseKey\":\"{5}\",\"hwid\":\"{6}\"}}",
                    Escape(this.name), Escape(this.ownerid), Escape(this.secret),
                    Escape(username), Escape(password), Escape(licenseKey), Escape(hwid)
                );

                string res = PostRequest("/register", payload);
                bool succ = GetBool(res, "success");
                response.success = succ;
                response.message = GetString(res, "message");

                if (succ)
                {
                    user_data.username = GetString(res, "username");
                    user_data.level = GetString(res, "level");
                    user_data.expires = GetString(res, "expiresAt");
                    user_data.token = GetString(res, "token");
                }
            }
            catch (Exception ex)
            {
                response.success = false;
                response.message = "Register error: " + ex.Message;
            }
        }

        public void license(string licenseKey)
        {
            if (!isInitialized)
            {
                init();
                if (!response.success) return;
            }

            try
            {
                string hwid = getHWID();
                string payload = string.Format(
                    "{{\"name\":\"{0}\",\"ownerid\":\"{1}\",\"secret\":\"{2}\",\"key\":\"{3}\",\"hwid\":\"{4}\"}}",
                    Escape(this.name), Escape(this.ownerid), Escape(this.secret),
                    Escape(licenseKey), Escape(hwid)
                );

                string res = PostRequest("/license", payload);
                bool succ = GetBool(res, "success");
                response.success = succ;
                response.message = GetString(res, "message");

                if (succ)
                {
                    user_data.username = licenseKey;
                    user_data.level = GetString(res, "level");
                    user_data.expires = GetString(res, "expiresAt");
                    user_data.token = GetString(res, "token");
                }
            }
            catch (Exception ex)
            {
                response.success = false;
                response.message = "License login error: " + ex.Message;
            }
        }

        public string getvar(string varName)
        {
            try
            {
                string res = GetRequest("/var/" + varName);
                return GetString(res, "value");
            }
            catch
            {
                return string.Empty;
            }
        }

        // ============================================
        // ZERO-DEPENDENCY HTTP CLIENT
        // ============================================

        private string PostRequest(string endpoint, string jsonBody)
        {
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(apiUrl + endpoint);
            request.Method = "POST";
            request.ContentType = "application/json; charset=utf-8";
            request.Timeout = 12000;
            request.Headers.Add("x-api-key", this.secret);
            request.Headers.Add("x-owner-id", this.ownerid);
            request.Headers.Add("x-app-name", this.name);

            byte[] bytes = Encoding.UTF8.GetBytes(jsonBody);
            request.ContentLength = bytes.Length;

            using (Stream os = request.GetRequestStream())
            {
                os.Write(bytes, 0, bytes.Length);
            }

            try
            {
                using (HttpWebResponse res = (HttpWebResponse)request.GetResponse())
                using (StreamReader reader = new StreamReader(res.GetResponseStream(), Encoding.UTF8))
                {
                    return reader.ReadToEnd();
                }
            }
            catch (WebException wex)
            {
                if (wex.Response != null)
                {
                    using (StreamReader reader = new StreamReader(wex.Response.GetResponseStream(), Encoding.UTF8))
                    {
                        return reader.ReadToEnd();
                    }
                }
                return string.Format("{{\"success\":false,\"message\":\"Connection error: {0}\"}}", Escape(wex.Message));
            }
        }

        private string GetRequest(string endpoint)
        {
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(apiUrl + endpoint);
            request.Method = "GET";
            request.Timeout = 10000;
            request.Headers.Add("x-api-key", this.secret);
            request.Headers.Add("x-owner-id", this.ownerid);
            request.Headers.Add("x-app-name", this.name);

            try
            {
                using (HttpWebResponse res = (HttpWebResponse)request.GetResponse())
                using (StreamReader reader = new StreamReader(res.GetResponseStream(), Encoding.UTF8))
                {
                    return reader.ReadToEnd();
                }
            }
            catch (WebException wex)
            {
                if (wex.Response != null)
                {
                    using (StreamReader reader = new StreamReader(wex.Response.GetResponseStream(), Encoding.UTF8))
                    {
                        return reader.ReadToEnd();
                    }
                }
                return string.Empty;
            }
        }

        // ============================================
        // ZERO-DEPENDENCY SAFE JSON EXTRACTORS
        // ============================================

        private static string Escape(string s)
        {
            if (string.IsNullOrEmpty(s)) return string.Empty;
            return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", "\\n");
        }

        private static string GetString(string json, string key)
        {
            if (string.IsNullOrEmpty(json)) return string.Empty;
            string pattern = "\"" + key + "\"";
            int idx = json.IndexOf(pattern);
            if (idx == -1) return string.Empty;

            int colon = json.IndexOf(':', idx + pattern.Length);
            if (colon == -1) return string.Empty;

            int start = colon + 1;
            while (start < json.Length && char.IsWhiteSpace(json[start])) start++;
            if (start >= json.Length) return string.Empty;

            if (json[start] == '\"')
            {
                int end = json.IndexOf('\"', start + 1);
                if (end != -1)
                {
                    return json.Substring(start + 1, end - start - 1);
                }
            }
            else
            {
                int end = start;
                while (end < json.Length && json[end] != ',' && json[end] != '}' && !char.IsWhiteSpace(json[end]))
                {
                    end++;
                }
                string val = json.Substring(start, end - start);
                return val == "null" ? string.Empty : val;
            }

            return string.Empty;
        }

        private static bool GetBool(string json, string key)
        {
            string val = GetString(json, key).ToLower();
            return val == "true" || val == "1";
        }

        // ============================================
        // MODELS
        // ============================================

        public class Response
        {
            public bool success { get; set; }
            public string message { get; set; }

            public Response()
            {
                this.success = false;
                this.message = string.Empty;
            }
        }

        public class UserData
        {
            public string username { get; set; }
            public string level { get; set; }
            public string expires { get; set; }
            public bool lifetime { get; set; }
            public string hwid { get; set; }
            public string token { get; set; }

            public UserData()
            {
                this.username = string.Empty;
                this.level = string.Empty;
                this.expires = string.Empty;
                this.lifetime = false;
                this.hwid = string.Empty;
                this.token = string.Empty;
            }
        }

        public class AppData
        {
            public string name { get; set; }
            public string version { get; set; }
            public string announcement { get; set; }
            public string downloadUrl { get; set; }

            public AppData()
            {
                this.name = string.Empty;
                this.version = string.Empty;
                this.announcement = string.Empty;
                this.downloadUrl = string.Empty;
            }
        }
    }
}
