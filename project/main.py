from color_analyzer import WristColorAnalyzer

# ====== CHANGE THIS TO  IMAGE FILE NAME ======
image_path ="IMG_1734.jpeg"
# ================================================

# Create object
analyzer = WristColorAnalyzer(image_path)

# Run analysis
result = analyzer.run_analysis()

# Print results
print("Analysis Result:")
print(result)

#Show all records in database
print("\nAll Database Records:")
print(analyzer.get_all_records())