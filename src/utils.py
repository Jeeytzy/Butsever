#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class User:
    """
    Kelas untuk mengambil detail user dari objek From_User
    """
    def __init__(self, user_obj):
        """
        Inisialisasi data user
        """
        self.id = user_obj.id
        self.username = user_obj.username
        self.first_name = user_obj.first_name
        self.last_name = user_obj.last_name
        
    @property
    def nama_lengkap(self):
        """
        Mengembalikan nama lengkap user
        """
        return str(self.first_name or self.last_name or self.username or self.id)


def ambil_token():
    """
    Fungsi untuk mengambil token bot dari file token.txt
    """
    try:
        with open("src/token.txt", "r", encoding="utf-8") as file:
            token = file.read().strip()
            if not token or token == "MASUKKAN_TOKEN_BOT_ANDA_DI_SINI":
                raise ValueError("Token bot belum diatur!")
            return token
    except FileNotFoundError:
        raise FileNotFoundError("File token.txt tidak ditemukan!")
    except Exception as e:
        raise Exception(f"Error membaca token: {str(e)}")