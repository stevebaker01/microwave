#!/usr/bin/env bash
mysql -u root --verbose microwave < flush_microwave.sql
mysql -u root --verbose microwave < flush_spotify.sql
mysql -u root --verbose microwave < flush_youtube.sql
