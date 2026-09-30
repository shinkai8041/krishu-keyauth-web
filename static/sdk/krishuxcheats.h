#pragma once
#ifndef KRISHU_X_CHEATS_H
#define KRISHU_X_CHEATS_H

#include <string>
#include <windows.h>
#include <wininet.h>

#pragma comment(lib, "wininet.lib")

namespace KrishuXCheats {

    struct Response {
        bool success;
        std::string message;

        Response() : success(false), message("") {}
    };

    struct UserData {
        std::string username;
        std::string level;
        std::string expires;
        bool lifetime;
        std::string hwid;
        std::string token;

        UserData() : username(""), level(""), expires(""), lifetime(false), hwid(""), token("") {}
    };

    struct AppData {
        std::string name;
        std::string version;
        std::string announcement;
        std::string downloadUrl;

        AppData() : name(""), version(""), announcement(""), downloadUrl("") {}
    };

    class api {
    public:
        std::string name;
        std::string ownerid;
        std::string secret;
        std::string version;
        std::string apiUrl;

        Response response;
        UserData user_data;
        AppData app_data;

        api(std::string name, std::string ownerid, std::string secret, std::string version, std::string apiUrl = "http://localhost:3000/api/v1");

        void init();
        void login(std::string username, std::string password);
        void registerUser(std::string username, std::string password, std::string licenseKey);
        void license(std::string licenseKey);
        std::string getvar(std::string varName);
        static std::string getHWID();

    private:
        bool isInitialized;
        std::string httpRequest(const std::string& endpoint, const std::string& method, const std::string& jsonBody);
        std::string extractJsonField(const std::string& json, const std::string& field);
        bool extractJsonBool(const std::string& json, const std::string& field);
        std::string escapeJson(const std::string& str);
    };
}

#endif // KRISHU_X_CHEATS_H
