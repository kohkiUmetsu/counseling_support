#!/usr/bin/env python3
"""
データベースマイグレーション実行スクリプト
ECSタスクから実行するため
"""
import os
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """マイグレーションを実行"""
    # Alembicの設定ファイルパス
    alembic_cfg = Config("alembic.ini")
    
    print("Running database migrations...")
    
    try:
        # マイグレーションを最新まで実行
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration completed successfully!")
        return 0
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = run_migrations()
    sys.exit(exit_code)