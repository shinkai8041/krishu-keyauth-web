/**
 * Krishu X Cheats — High-Performance Zero-Dependency Java SDK
 * 
 * Works out-of-the-box in:
 * - Java 8, 11, 17, 21+
 * - Android (API 21+)
 * - Swing / JavaFX / Console Loaders
 * 
 * NO EXTERNAL LIBRARIES OR MAVEN DEPENDENCIES REQUIRED!
 * (If your project uses a package declaration, add it to line 1)
 */

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

public class KrishuXCheats {

    public static class Response {
        public boolean success = false;
        public String message = "";
    }

    public static class UserData {
        public String username = "";
        public String level = "";
        public String expires = "";
        public boolean lifetime = false;
        public String hwid = "";
        public String token = "";
    }

    public static class AppData {
        public String name = "";
        public String version = "";
        public String announcement = "";
        public String downloadUrl = "";
    }

    public static class api {
        public String name;
        public String ownerid;
        public String secret;
        public String version;
        public String apiUrl;

        public Response response = new Response();
        public UserData user_data = new UserData();
        public AppData app_data = new AppData();

        private boolean isInitialized = false;

        public api(String name, String ownerid, String secret, String version) {
            this(name, ownerid, secret, version, "http://localhost:3000/api/v1");
        }

        public api(String name, String ownerid, String secret, String version, String apiUrl) {
            this.name = name != null ? name : "";
            this.ownerid = ownerid != null ? ownerid : "";
            this.secret = secret != null ? secret : "";
            this.version = version != null ? version : "1.0.0";
            this.apiUrl = apiUrl != null ? apiUrl.replaceAll("/+$", "") : "http://localhost:3000/api/v1";
        }

        public static String getHWID() {
            try {
                String toHash = System.getProperty("os.name", "") +
                                System.getProperty("os.arch", "") +
                                System.getProperty("user.name", "") +
                                System.getenv("PROCESSOR_IDENTIFIER");
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                byte[] hash = md.digest(toHash.getBytes(StandardCharsets.UTF_8));
                StringBuilder hex = new StringBuilder();
                for (byte b : hash) {
                    hex.append(String.format("%02x", b));
                }
                return hex.substring(0, 32);
            } catch (Exception e) {
                return "HWID-JAVA-GENERIC";
            }
        }

        private String request(String endpoint, String method, String jsonBody) {
            try {
                URL url = new URL(this.apiUrl + endpoint);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod(method);
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                conn.setRequestProperty("x-api-key", this.secret);
                conn.setRequestProperty("x-owner-id", this.ownerid);
                conn.setRequestProperty("x-app-name", this.name);
                conn.setRequestProperty("User-Agent", "KrishuXCheats-Java/1.0");
                conn.setConnectTimeout(12000);
                conn.setReadTimeout(12000);

                if (jsonBody != null && !jsonBody.isEmpty()) {
                    conn.setDoOutput(true);
                    try (OutputStream os = conn.getOutputStream()) {
                        byte[] input = jsonBody.getBytes(StandardCharsets.UTF_8);
                        os.write(input, 0, input.length);
                    }
                }

                int code = conn.getResponseCode();
                BufferedReader br = new BufferedReader(new InputStreamReader(
                        code >= 200 && code < 300 ? conn.getInputStream() : conn.getErrorStream(),
                        StandardCharsets.UTF_8
                ));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }
                return sb.toString();
            } catch (Exception e) {
                return "{\"success\":false,\"message\":\"Connection error: " + e.getMessage() + "\"}";
            }
        }

        private String parseField(String json, String field) {
            if (json == null) return "";
            String target = "\"" + field + "\"";
            int idx = json.indexOf(target);
            if (idx == -1) return "";
            int colon = json.indexOf(":", idx + target.length());
            if (colon == -1) return "";
            int start = colon + 1;
            while (start < json.Length && Character.isWhitespace(json.charAt(start))) start++;
            if (start >= json.length()) return "";

            if (json.charAt(start) == '\"') {
                int end = json.indexOf("\"", start + 1);
                if (end != -1) return json.substring(start + 1, end);
            } else {
                int end = start;
                while (end < json.length() && json.charAt(end) != ',' && json.charAt(end) != '}' && !Character.isWhitespace(json.charAt(end))) end++;
                String val = json.substring(start, end);
                return "null".equals(val) ? "" : val;
            }
            return "";
        }

        private String escape(String s) {
            if (s == null) return "";
            return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\r", "").replace("\n", "\\n");
        }

        public void init() {
            String body = String.format("{\"name\":\"%s\",\"ownerid\":\"%s\",\"secret\":\"%s\",\"version\":\"%s\"}",
                    escape(name), escape(ownerid), escape(secret), escape(version));
            String res = request("/init", "POST", body);

            response.success = "true".equalsIgnoreCase(parseField(res, "success"));
            response.message = parseField(res, "message");

            if (response.success) {
                isInitialized = true;
                app_data.name = parseField(res, "name");
                app_data.version = parseField(res, "version");
                app_data.announcement = parseField(res, "announcement");
                app_data.downloadUrl = parseField(res, "downloadUrl");
            }
        }

        public void login(String username, String password) {
            if (!isInitialized) {
                response.success = false;
                response.message = "Please initialize API before calling login()";
                return;
            }

            String hwid = getHWID();
            String body = String.format("{\"name\":\"%s\",\"ownerid\":\"%s\",\"secret\":\"%s\",\"username\":\"%s\",\"password\":\"%s\",\"hwid\":\"%s\"}",
                    escape(name), escape(ownerid), escape(secret), escape(username), escape(password), escape(hwid));

            String res = request("/login", "POST", body);

            response.success = "true".equalsIgnoreCase(parseField(res, "success"));
            response.message = parseField(res, "message");

            if (response.success) {
                user_data.username = parseField(res, "username");
                user_data.level = parseField(res, "level");
                user_data.expires = parseField(res, "expiresAt");
                if (user_data.expires.isEmpty() || "null".equals(user_data.expires)) {
                    user_data.expires = "Lifetime";
                    user_data.lifetime = true;
                } else {
                    user_data.lifetime = "true".equalsIgnoreCase(parseField(res, "lifetime"));
                }
                user_data.hwid = parseField(res, "hwid");
                user_data.token = parseField(res, "token");
            }
        }

        public void register(String username, String password, string licenseKey) {
            if (!isInitialized) {
                response.success = false;
                response.message = "Please initialize API before calling register()";
                return;
            }

            String hwid = getHWID();
            String body = String.format("{\"name\":\"%s\",\"ownerid\":\"%s\",\"secret\":\"%s\",\"username\":\"%s\",\"password\":\"%s\",\"licenseKey\":\"%s\",\"hwid\":\"%s\"}",
                    escape(name), escape(ownerid), escape(secret), escape(username), escape(password), escape(licenseKey), escape(hwid));

            String res = request("/register", "POST", body);

            response.success = "true".equalsIgnoreCase(parseField(res, "success"));
            response.message = parseField(res, "message");

            if (response.success) {
                user_data.username = parseField(res, "username");
                user_data.level = parseField(res, "level");
                user_data.expires = parseField(res, "expiresAt");
                user_data.token = parseField(res, "token");
            }
        }

        public void license(String licenseKey) {
            if (!isInitialized) {
                response.success = false;
                response.message = "Please initialize API before calling license()";
                return;
            }

            String hwid = getHWID();
            String body = String.format("{\"name\":\"%s\",\"ownerid\":\"%s\",\"secret\":\"%s\",\"key\":\"%s\",\"hwid\":\"%s\"}",
                    escape(name), escape(ownerid), escape(secret), escape(licenseKey), escape(hwid));

            String res = request("/license", "POST", body);

            response.success = "true".equalsIgnoreCase(parseField(res, "success"));
            response.message = parseField(res, "message");

            if (response.success) {
                user_data.username = licenseKey;
                user_data.level = parseField(res, "level");
                user_data.expires = parseField(res, "expiresAt");
                user_data.token = parseField(res, "token");
            }
        }

        public String getvar(String varName) {
            String res = request("/var/" + varName, "GET", null);
            return parseField(res, "value");
        }
    }
}
