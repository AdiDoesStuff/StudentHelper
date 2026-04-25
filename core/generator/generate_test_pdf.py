import fitz

doc = fitz.open()

# Page 1
page1 = doc.new_page()
text1 = "Electrostatics is the branch of physics that deals with the study of stationary electric charges or fields. The fundamental concept is Coulomb's Law, which states that the electrostatic force between two point charges is directly proportional to the product of their magnitudes and inversely proportional to the square of the distance between them."
page1.insert_text((50, 50), text1, fontsize=12)

# Page 2
page2 = doc.new_page()
text2 = "Electric flux is the measure of the electric field lines crossing a given area. According to Gauss's Law, the net electric flux through any closed surface is equal to the net charge enclosed by the surface divided by the vacuum permittivity."
page2.insert_text((50, 50), text2, fontsize=12)

doc.save("test_electrostatics.pdf")
doc.close()
print("test_electrostatics.pdf created successfully.")
