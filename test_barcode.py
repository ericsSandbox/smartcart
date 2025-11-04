#!/usr/bin/env python3
"""
Barcode Detection Test Script
Tests multiple barcode detection methods on the provided image
"""

import sys
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

# Try to import barcode libraries
try:
    from pyzbar import pyzbar
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False
    print("⚠️ pyzbar not available")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️ requests not available")


def test_image_properties(image_path):
    """Analyze image properties"""
    print("\n" + "="*60)
    print("📊 IMAGE ANALYSIS")
    print("="*60)
    
    img = Image.open(image_path)
    print(f"✅ Image loaded: {image_path}")
    print(f"   Size: {img.size[0]}x{img.size[1]} pixels")
    print(f"   Mode: {img.mode}")
    print(f"   Format: {img.format}")
    
    # Convert to numpy for analysis
    img_array = np.array(img)
    print(f"   Array shape: {img_array.shape}")
    
    # Analyze for barcode characteristics
    if img.mode == 'RGB':
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    elif img.mode == 'RGBA':
        gray = cv2.cvtColor(img_array[:,:,:3], cv2.COLOR_RGB2GRAY)
    else:
        gray = np.array(img.convert('L'))
    
    # Check contrast
    mean_val = np.mean(gray)
    std_val = np.std(gray)
    print(f"\n📈 Contrast Analysis:")
    print(f"   Mean brightness: {mean_val:.1f}")
    print(f"   Std deviation: {std_val:.1f}")
    
    if std_val < 10:
        print("   ⚠️  LOW contrast - barcode may be hard to read")
    else:
        print("   ✅ Good contrast")
    
    return gray


def test_pyzbar(image_path):
    """Test with pyzbar library"""
    print("\n" + "="*60)
    print("🔍 PYZBAR DETECTION")
    print("="*60)
    
    if not HAS_PYZBAR:
        print("❌ pyzbar not installed")
        return None
    
    try:
        img = Image.open(image_path)
        barcodes = pyzbar.decode(img)
        
        if barcodes:
            print(f"✅ FOUND {len(barcodes)} BARCODE(S):")
            for barcode in barcodes:
                print(f"   Type: {barcode.type}")
                print(f"   Data: {barcode.data.decode('utf-8')}")
                print(f"   Quality: {barcode.quality}")
            return barcodes[0].data.decode('utf-8')
        else:
            print("❌ No barcodes detected")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_opencv_processing(image_path):
    """Test with OpenCV preprocessing"""
    print("\n" + "="*60)
    print("🔬 OPENCV PREPROCESSING + PYZBAR")
    print("="*60)
    
    if not HAS_PYZBAR:
        print("❌ pyzbar not installed")
        return None
    
    try:
        # Load image
        img_cv = cv2.imread(str(image_path))
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Try multiple preprocessing approaches
        approaches = [
            ("Original", gray),
            ("Threshold (127)", cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]),
            ("Adaptive Threshold", cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
            ("Clahe", cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)),
        ]
        
        best_result = None
        
        for approach_name, processed_img in approaches:
            print(f"\n  Testing {approach_name}...")
            
            # Convert back to PIL for pyzbar
            pil_img = Image.fromarray(processed_img)
            barcodes = pyzbar.decode(pil_img)
            
            if barcodes:
                print(f"    ✅ SUCCESS! Found: {barcodes[0].data.decode('utf-8')}")
                best_result = barcodes[0].data.decode('utf-8')
                break
            else:
                print(f"    ⚠️  No detection")
        
        if not best_result:
            print("\n  ❌ No approach succeeded")
        
        return best_result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_manual_barcode_detection(image_path):
    """Manual edge detection approach"""
    print("\n" + "="*60)
    print("🎯 MANUAL BARCODE DETECTION (Edge Analysis)")
    print("="*60)
    
    try:
        img_cv = cv2.imread(str(image_path))
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for vertical lines (barcode characteristic)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
        
        # Count vertical line pixels
        line_count = np.sum(vertical_lines) / 255
        
        print(f"  Vertical line pixels detected: {line_count:.0f}")
        
        if line_count > 1000:
            print(f"  ✅ Strong barcode pattern detected!")
            return True
        else:
            print(f"  ⚠️  Weak or no barcode pattern")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    # Find the barcode image
    search_paths = [
        Path('/home/eric/Projects/SmartCart/justbarcode.jpg'),
        Path('/tmp/barcode.jpg'),
        Path('/tmp/smartcart-netlify/barcode.jpg'),
    ]
    
    image_path = None
    for path in search_paths:
        if path.exists():
            image_path = path
            break
    
    if not image_path:
        print("❌ Could not find barcode image")
        print(f"Searched: {search_paths}")
        sys.exit(1)
    
    print("\n🚀 BARCODE DETECTION TEST SUITE")
    print("Testing barcode detection with multiple methods\n")
    print(f"Image: {image_path}")
    
    # Test 1: Image analysis
    gray = test_image_properties(image_path)
    
    # Test 2: Direct pyzbar
    result1 = test_pyzbar(image_path)
    
    # Test 3: OpenCV preprocessing
    result2 = test_opencv_processing(image_path)
    
    # Test 4: Manual detection
    result3 = test_manual_barcode_detection(image_path)
    
    # Summary
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    
    if result1:
        print(f"✅ Direct pyzbar: SUCCESS - {result1}")
    else:
        print(f"❌ Direct pyzbar: FAILED")
    
    if result2:
        print(f"✅ OpenCV+pyzbar: SUCCESS - {result2}")
    else:
        print(f"❌ OpenCV+pyzbar: FAILED")
    
    if result3:
        print(f"✅ Manual edge detection: FOUND PATTERN")
    else:
        print(f"❌ Manual edge detection: NO PATTERN")
    
    print("\n" + "="*60)
    if result1 or result2:
        print("🎉 BARCODE CAN BE DETECTED BY PYTHON LIBRARIES")
        print("Issue is likely with JavaScript library implementation")
    else:
        print("⚠️  Even Python libraries can't detect - image issue?")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
