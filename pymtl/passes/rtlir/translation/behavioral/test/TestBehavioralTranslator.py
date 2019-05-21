#=========================================================================
# TestBehavioralTranslator.py
#=========================================================================
# Author : Peitian Pan
# Date   : May 20, 2019
"""Provide a behavioral translator that fits testing purposes."""

from __future__ import absolute_import, division, print_function


def mk_TestBehavioralTranslator( _BehavioralTranslator ):
  def make_indent( src, nindent ):
    """Add nindent indention to every line in src."""
    indent = '  '
    for idx, s in enumerate( src ):
      src[ idx ] = nindent * indent + s

  class TestBehavioralTranslator( _BehavioralTranslator ):
    def rtlir_data_type_translation( s, m, dtype ):
      return str(dtype)

    def rtlir_tr_upblk_decls( s, upblk_srcs ):
      srcs = ''
      for upblk_src in upblk_srcs:
        make_indent( upblk_src, 1 )
        srcs += '\n' + '\n'.join( upblk_src )
      return 'upblk_decls:{}\n'.format( srcs )

    def rtlir_tr_upblk_decl( m, upblk, rtlir_upblk ):
      return ['upblk_decl: {}'.format( rtlir_upblk.name )]

    def rtlir_tr_behavioral_freevars( s, freevars ):
      srcs = ''
      for freevar in freevars:
        make_indent( freevar, 1 )
        srcs += '\n' + '\n'.join( freevar )
      return 'freevars:{}\n'.format( srcs )

    def rtlir_tr_behavioral_freevar( s, id_, rtype, array_type, dtype, obj ):
      return ['freevar: {id_}'.format( **locals() )]

    def rtlir_tr_behavioral_tmpvars( s, tmpvars ):
      srcs = ''
      for tmpvar in tmpvars:
        make_indent( tmpvar, 1 )
        srcs += '\n' + '\n'.join( tmpvar )
      return 'tmpvars:{}\n'.format( srcs )

    def rtlir_tr_behavioral_tmpvar( s, id_, upblk_id, dtype ):
      return ['tmpvar: {id_} in {upblk_id} of {dtype}'.format( **locals() )]

    def rtlir_tr_unpacked_array_type( s, array_rtype ):
      return 'unpacked_array: {}'.format( array_rtype )

    def rtlir_tr_vector_dtype( s, dtype ):
      return 'vector: {}'.format( dtype )

  return TestBehavioralTranslator
