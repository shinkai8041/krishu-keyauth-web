#include "krishuxcheats.h"
#include <iostream>
#include <sstream>
#include <vector>

namespace KrishuXCheats {

    api::api(std::string name, std::string ownerid, std::string secret, std::string version, std::string apiUrl)
        : name(name), ownerid(ownerid), secret(secret), version(version), isInitialized(false) {
        // Strip trailing slashes
        while (!apiUrl.empty() && (apiUrl.back() == '/' || apiUrl.back() == '\\')) {
            apiUrl.pop_back();
        }
        this->apiUrl = apiUrl.empty() ? "http://localhost:3000/api/v1" : apiUrl;
    }

    std::string api::getHWID() {
        HW_PROFILE_INFO hwProfileInfo;
        if (GetCurrentHwProfileA(&hwProfileInfo)) {
            std::string guid = hwProfileInfo.szHwProfileGuid;
            if (!guid.empty()) return guid;
        }

        DWORD volumeSerial = 0;
        if (GetVolumeInformationA("C:\\", NULL, 0, &volumeSerial, NULL, NULL, NULL, 0)) {
            char serialStr[64];
            sprintf_s(serialStr, "%08X", volumeSerial);
            return std::string("HWID-") + serialStr;
        }

        char compName[MAX_COMPUTERNAME_LENGTH + 1];
        DWORD size = sizeof(compName);
        if (GetComputerNameA(compName, &size)) {
            return std::string("HWID-") + compName;
        }

        return "HWID-CPP-GENERIC";
    }

    std::string api::escapeJson(const std::string& str) {
        std::ostringstream ss;
        for (char c : str) {
            switch (c) {
                case '\"': ss << "\\\""; break;
                case '\\': ss << "\\\\"; break;
                case '\b': ss << "\\b";  break;
                case '\f': ss << "\\f";  break;
                case '\n': ss << "\\n";  break;
                case '\r': ss << "\\r";  break;
                case '\t': ss << "\\t";  break;
                default:   ss << c;       break;
            }
        }
        return ss.str();
    }

    std::string api::extractJsonField(const std::string& json, const std::string& field) {
        std::string search = "\"" + field + "\"";
        size_t pos = json.find(search);
        if (pos == std::string::npos) return "";

        size_t colon = json.find(":", pos + search.length());
        if (colon == std::string::npos) return "";

        size_t start = json.find_first_not_of(" \t\n\r", colon + 1);
        if (start == std::string::npos) return "";

        if (json[start] == '\"') {
            size_t end = json.find("\"", start + 1);
            if (end != std::string::npos) {
                return json.substr(start + 1, end - start - 1);
            }
        } else {
            size_t end = json.find_first_of(",}\n\r", start);
            if (end != std::string::npos) {
                std::string val = json.substr(start, end - start);
                size_t last = val.find_last_not_of(" \t\n\r");
                if (last != std::string::npos) {
                    val = val.substr(0, last + 1);
                }
                return val == "null" ? "" : val;
            }
        }
        return "";
    }

    bool api::extractJsonBool(const std::string& json, const std::string& field) {
        std::string val = extractJsonField(json, field);
        return val == "true" || val == "1";
    }

    std::string api::httpRequest(const std::string& endpoint, const std::string& method, const std::string& jsonBody) {
        HINTERNET hInternet = InternetOpenA("KrishuXCheats-CPP/1.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
        if (!hInternet) return "{\"success\":false,\"message\":\"InternetOpen failed\"}";

        bool isHttps = (apiUrl.rfind("https://", 0) == 0);
        std::string host = "localhost";
        INTERNET_PORT port = isHttps ? 443 : 3000;
        std::string basePath = "/api/v1";

        std::string urlToParse = apiUrl;
        size_t protoPos = urlToParse.find("://");
        if (protoPos != std::string::npos) {
            urlToParse = urlToParse.substr(protoPos + 3);
        }

        size_t slashPos = urlToParse.find('/');
        std::string hostPort = (slashPos != std::string::npos) ? urlToParse.substr(0, slashPos) : urlToParse;
        basePath = (slashPos != std::string::npos) ? urlToParse.substr(slashPos) : "";

        size_t colonPos = hostPort.find(':');
        if (colonPos != std::string::npos) {
            host = hostPort.substr(0, colonPos);
            try {
                port = (INTERNET_PORT)std::stoi(hostPort.substr(colonPos + 1));
            } catch (...) {
                port = isHttps ? 443 : 80;
            }
        } else {
            host = hostPort;
            port = isHttps ? 443 : 80;
        }

        std::string fullPath = basePath + endpoint;

        DWORD flags = INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE;
        if (isHttps || port == 443) {
            flags |= INTERNET_FLAG_SECURE | INTERNET_FLAG_IGNORE_CERT_CN_INVALID | INTERNET_FLAG_IGNORE_CERT_DATE_INVALID;
        }

        HINTERNET hConnect = InternetConnectA(hInternet, host.c_str(), port, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
        if (!hConnect) {
            InternetCloseHandle(hInternet);
            return "{\"success\":false,\"message\":\"Connection to server failed\"}";
        }

        HINTERNET hRequest = HttpOpenRequestA(hConnect, method.c_str(), fullPath.c_str(), NULL, NULL, NULL, flags, 0);
        if (!hRequest) {
            InternetCloseHandle(hConnect);
            InternetCloseHandle(hInternet);
            return "{\"success\":false,\"message\":\"HttpOpenRequest failed\"}";
        }

        if (isHttps || port == 443) {
            DWORD secFlags = SECURITY_FLAG_IGNORE_UNKNOWN_CA | SECURITY_FLAG_IGNORE_CERT_DATE_INVALID | SECURITY_FLAG_IGNORE_CERT_CN_INVALID | SECURITY_FLAG_IGNORE_REVOCATION;
            InternetSetOptionA(hRequest, INTERNET_OPTION_SECURITY_FLAGS, &secFlags, sizeof(secFlags));
        }

        std::string headers = "Content-Type: application/json; charset=utf-8\r\n";
        headers += "x-api-key: " + secret + "\r\n";
        headers += "x-owner-id: " + ownerid + "\r\n";
        headers += "x-app-name: " + name + "\r\n";

        LPVOID bodyData = jsonBody.empty() ? NULL : (LPVOID)jsonBody.c_str();
        DWORD bodyLen = (DWORD)jsonBody.length();

        BOOL sent = HttpSendRequestA(hRequest, headers.c_str(), (DWORD)headers.length(), bodyData, bodyLen);
        if (!sent) {
            InternetCloseHandle(hRequest);
            InternetCloseHandle(hConnect);
            InternetCloseHandle(hInternet);
            return "{\"success\":false,\"message\":\"HttpSendRequest failed\"}";
        }

        std::string responseStr = "";
        char buffer[4096];
        DWORD bytesRead = 0;
        while (InternetReadFile(hRequest, buffer, sizeof(buffer) - 1, &bytesRead) && bytesRead > 0) {
            buffer[bytesRead] = '\0';
            responseStr += buffer;
        }

        InternetCloseHandle(hRequest);
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hInternet);

        return responseStr;
    }

    void api::init() {
        std::string body = "{\"name\":\"" + escapeJson(name) + "\",\"ownerid\":\"" + escapeJson(ownerid) + "\",\"secret\":\"" + escapeJson(secret) + "\",\"version\":\"" + escapeJson(version) + "\"}";
        std::string res = httpRequest("/init", "POST", body);

        response.success = extractJsonBool(res, "success");
        response.message = extractJsonField(res, "message");

        if (response.success) {
            isInitialized = true;
            app_data.name = extractJsonField(res, "name");
            app_data.version = extractJsonField(res, "version");
            app_data.announcement = extractJsonField(res, "announcement");
            app_data.downloadUrl = extractJsonField(res, "downloadUrl");
        }
    }

    void api::login(std::string username, std::string password) {
        if (!isInitialized) {
            response.success = false;
            response.message = "Please initialize API before calling login()";
            return;
        }

        std::string hwid = getHWID();
        std::string body = "{\"name\":\"" + escapeJson(name) + "\",\"ownerid\":\"" + escapeJson(ownerid) + "\",\"secret\":\"" + escapeJson(secret) + "\",\"username\":\"" + escapeJson(username) + "\",\"password\":\"" + escapeJson(password) + "\",\"hwid\":\"" + escapeJson(hwid) + "\"}";

        std::string res = httpRequest("/login", "POST", body);

        response.success = extractJsonBool(res, "success");
        response.message = extractJsonField(res, "message");

        if (response.success) {
            user_data.username = extractJsonField(res, "username");
            user_data.level = extractJsonField(res, "level");
            user_data.expires = extractJsonField(res, "expiresAt");
            if (user_data.expires.empty() || user_data.expires == "null") {
                user_data.expires = "Lifetime";
                user_data.lifetime = true;
            } else {
                user_data.lifetime = extractJsonBool(res, "lifetime");
            }
            user_data.hwid = extractJsonField(res, "hwid");
            user_data.token = extractJsonField(res, "token");
        }
    }

    void api::registerUser(std::string username, std::string password, std::string licenseKey) {
        if (!isInitialized) {
            response.success = false;
            response.message = "Please initialize API before calling registerUser()";
            return;
        }

        std::string hwid = getHWID();
        std::string body = "{\"name\":\"" + escapeJson(name) + "\",\"ownerid\":\"" + escapeJson(ownerid) + "\",\"secret\":\"" + escapeJson(secret) + "\",\"username\":\"" + escapeJson(username) + "\",\"password\":\"" + escapeJson(password) + "\",\"licenseKey\":\"" + escapeJson(licenseKey) + "\",\"hwid\":\"" + escapeJson(hwid) + "\"}";

        std::string res = httpRequest("/register", "POST", body);

        response.success = extractJsonBool(res, "success");
        response.message = extractJsonField(res, "message");

        if (response.success) {
            user_data.username = extractJsonField(res, "username");
            user_data.level = extractJsonField(res, "level");
            user_data.expires = extractJsonField(res, "expiresAt");
            user_data.token = extractJsonField(res, "token");
        }
    }

    void api::license(std::string licenseKey) {
        if (!isInitialized) {
            response.success = false;
            response.message = "Please initialize API before calling license()";
            return;
        }

        std::string hwid = getHWID();
        std::string body = "{\"name\":\"" + escapeJson(name) + "\",\"ownerid\":\"" + escapeJson(ownerid) + "\",\"secret\":\"" + escapeJson(secret) + "\",\"key\":\"" + escapeJson(licenseKey) + "\",\"hwid\":\"" + escapeJson(hwid) + "\"}";

        std::string res = httpRequest("/license", "POST", body);

        response.success = extractJsonBool(res, "success");
        response.message = extractJsonField(res, "message");

        if (response.success) {
            user_data.username = licenseKey;
            user_data.level = extractJsonField(res, "level");
            user_data.expires = extractJsonField(res, "expiresAt");
            user_data.token = extractJsonField(res, "token");
        }
    }

    std::string api::getvar(std::string varName) {
        std::string res = httpRequest("/var/" + varName, "GET", "");
        return extractJsonField(res, "value");
    }
}
