#!/bin/bash
set -e

echo "=================================================="
echo "    DramaDownloader iOS - Build IPA Script       "
echo "=================================================="

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "Lỗi: Không tìm thấy xcodebuild. Bạn cần cài đặt Xcode trên máy Mac."
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")/DramaDownloader" && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
ARCHIVE_PATH="$BUILD_DIR/DramaDownloader.xcarchive"
OUTPUT_DIR="$(cd "$(dirname "$0")" && pwd)/dist_ios"

mkdir -p "$OUTPUT_DIR"
cd "$PROJECT_DIR"

echo "1. Đang biên dịch mã nguồn (Archive)..."
xcodebuild archive \
    -project DramaDownloader.xcodeproj \
    -scheme DramaDownloader \
    -configuration Release \
    -archivePath "$ARCHIVE_PATH" \
    -destination "generic/platform=iOS" \
    CODE_SIGNING_ALLOWED=NO

echo "2. Đang tạo cấu trúc Payload..."
PAYLOAD_DIR="$BUILD_DIR/Payload"
rm -rf "$PAYLOAD_DIR"
mkdir -p "$PAYLOAD_DIR"
cp -r "$ARCHIVE_PATH/Products/Applications/DramaDownloader.app" "$PAYLOAD_DIR/"

echo "3. Đang nén thành tệp DramaDownloader.ipa..."
cd "$BUILD_DIR"
zip -r -q "$OUTPUT_DIR/DramaDownloader.ipa" Payload

echo "=================================================="
echo "✔ HOÀN TẤT! File cài đặt iOS đã sẵn sàng tại:"
echo "$OUTPUT_DIR/DramaDownloader.ipa"
echo "Bạn có thể dùng AltStore, Sideloadly hoặc TrollStore để cài vào iPhone."
echo "=================================================="

