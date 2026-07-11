/*
 * No-op stubs for the freetype/fontconfig symbols that libcairo.a's monolithic
 * cairo.c.o drags in via cairo_select_font_face -> cairo_toy_font_face_create
 * -> cairo-ft-font.c.o. transplot never renders text, so this code is dead at
 * runtime -- these definitions exist only to satisfy the static linker without
 * needing libfreetype.a / libfontconfig.a (which are not available as static
 * archives in the conda env).
 *
 * Derived from the undefined FT_ and Fc symbols of the cairo font objects that
 * enter the static link closure. The return type is irrelevant for linking
 * (C has no signature-based name mangling); each returns 0 and is never called.
 */

long FT_Bitmap_Convert(void) { return 0; }
long FT_Bitmap_Done(void) { return 0; }
long FT_Bitmap_New(void) { return 0; }
long FT_Done_Face(void) { return 0; }
long FT_Done_FreeType(void) { return 0; }
long FT_Done_MM_Var(void) { return 0; }
long FT_Get_Color_Glyph_Layer(void) { return 0; }
long FT_Get_First_Char(void) { return 0; }
long FT_Get_Font_Format(void) { return 0; }
long FT_Get_Glyph_Name(void) { return 0; }
long FT_Get_MM_Var(void) { return 0; }
long FT_Get_Next_Char(void) { return 0; }
long FT_Get_Var_Blend_Coordinates(void) { return 0; }
long FT_Get_Var_Design_Coordinates(void) { return 0; }
long FT_GlyphSlot_Embolden(void) { return 0; }
long FT_GlyphSlot_Oblique(void) { return 0; }
long FT_Init_FreeType(void) { return 0; }
long FT_Library_SetLcdFilter(void) { return 0; }
long FT_Load_Glyph(void) { return 0; }
long FT_Load_Sfnt_Table(void) { return 0; }
long FT_New_Face(void) { return 0; }
long FT_Outline_Decompose(void) { return 0; }
long FT_Outline_Get_CBox(void) { return 0; }
long FT_Outline_Transform(void) { return 0; }
long FT_Outline_Translate(void) { return 0; }
long FT_Palette_Data_Get(void) { return 0; }
long FT_Palette_Select(void) { return 0; }
long FT_Palette_Set_Foreground_Color(void) { return 0; }
long FT_Render_Glyph(void) { return 0; }
long FT_Set_Char_Size(void) { return 0; }
long FT_Set_Transform(void) { return 0; }
long FT_Set_Var_Design_Coordinates(void) { return 0; }
long FT_Vector_Transform(void) { return 0; }
long FcConfigGetCurrent(void) { return 0; }
long FcConfigSubstitute(void) { return 0; }
long FcDefaultSubstitute(void) { return 0; }
long FcFontMatch(void) { return 0; }
long FcFreeTypeCharIndex(void) { return 0; }
long FcInitBringUptoDate(void) { return 0; }
long FcPatternAddBool(void) { return 0; }
long FcPatternAddDouble(void) { return 0; }
long FcPatternAddInteger(void) { return 0; }
long FcPatternAddString(void) { return 0; }
long FcPatternCreate(void) { return 0; }
long FcPatternDel(void) { return 0; }
long FcPatternDestroy(void) { return 0; }
long FcPatternDuplicate(void) { return 0; }
long FcPatternGet(void) { return 0; }
long FcPatternGetBool(void) { return 0; }
long FcPatternGetFTFace(void) { return 0; }
long FcPatternGetInteger(void) { return 0; }
long FcPatternGetString(void) { return 0; }
