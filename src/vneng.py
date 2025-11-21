#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time


class VNEngine:
    """
    Virtual Number Engine - Mesin untuk mengambil nomor virtual
    """
    
    def __init__(self):
        """
        Inisialisasi variabel engine
        """
        self.lang = "?lang=en"
        self.base = "https://onlinesim.io/"
        self.endpoint = "api/v1/free_numbers_content/"
        self.country_url = f"{self.base}{self.endpoint}countries"
        self.timeout = 10
        
    def _request_with_retry(self, url, max_retries=3):
        """
        Melakukan request dengan retry jika gagal
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    return None
                time.sleep(1)
            except requests.exceptions.RequestException:
                if attempt == max_retries - 1:
                    return None
                time.sleep(1)
        return None

    def ambil_negara_online(self):
        """
        Mengambil daftar negara yang tersedia dan online
        """
        try:
            response = self._request_with_retry(self.country_url)
            
            if not response or response.get("response") != "1":
                return []
            
            semua_negara = response.get("counties", [])
            
            # Filter negara yang online saja
            negara_online = [
                negara for negara in semua_negara 
                if negara.get("online") == True
            ]
            
            return negara_online
            
        except Exception as e:
            print(f"Error mengambil negara: {str(e)}")
            return []

    def ambil_nomor_negara(self, negara):
        """
        Mengambil nomor dari negara tertentu
        """
        try:
            url_nomor = f"{self.country_url}/{negara}{self.lang}"
            response = self._request_with_retry(url_nomor)
            
            if not response or response.get("response") != "1":
                return []
            
            nomor_list = response.get("numbers", [])
            
            # Extract data waktu dan nomor
            nomor_hasil = [
                (nomor.get("data_humans"), nomor.get("full_number"))
                for nomor in nomor_list
                if nomor.get("full_number")
            ]
            
            return nomor_hasil
            
        except Exception as e:
            print(f"Error mengambil nomor negara {negara}: {str(e)}")
            return []

    def ambil_inbox_nomor(self, negara, nomor):
        """
        Mengambil inbox pesan dari nomor tertentu
        """
        try:
            url_detail = f"{self.country_url}/{negara}/{nomor}{self.lang}"
            response = self._request_with_retry(url_detail)
            
            if not response or response.get("response") != "1":
                return []
            
            if not response.get("online"):
                return []
            
            # Ambil pesan dari inbox
            pesan_data = response.get("messages", {}).get("data", [])
            
            pesan_list = [
                {pesan.get("data_humans"): pesan.get("text")}
                for pesan in pesan_data
                if pesan.get("text")
            ]
            
            return pesan_list
            
        except Exception as e:
            print(f"Error mengambil inbox nomor {nomor}: {str(e)}")
            return []
    
    def cek_nomor_valid(self, negara, nomor):
        """
        Mengecek apakah nomor masih valid dan online
        """
        try:
            inbox = self.ambil_inbox_nomor(negara, nomor)
            return inbox is not None and len(inbox) >= 0
        except:
            return False